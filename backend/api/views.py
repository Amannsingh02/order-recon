import csv
import io
import json
from decimal import Decimal, InvalidOperation

from django.db import transaction, models
from django.contrib.auth.models import User
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
import pandas as pd
from openai import OpenAI
from django.conf import settings

from .models import Order, Payment, ReconciliationResult
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    OrderSerializer,
    PaymentSerializer,
    ReconciliationResultSerializer,
    DashboardSummarySerializer,
)

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.check_password(password):
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    return Response({
        'user': UserSerializer(user).data,
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    return Response(UserSerializer(request.user).data)


# ---------------------------------------------------------------------------
# Data ingestion
# ---------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_orders(request):
    file = request.FILES.get('file')
    if not file:
        return Response({'detail': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    # Clear existing data for this user
    user.orders.all().delete()

    try:
        df = pd.read_csv(file)
        required_cols = {'order_id', 'order_date', 'customer_email', 'currency', 'gross_amount', 'discount', 'net_amount', 'status'}
        if not required_cols.issubset(set(df.columns)):
            missing = required_cols - set(df.columns)
            return Response({'detail': f'Missing columns: {missing}'}, status=status.HTTP_400_BAD_REQUEST)

        orders = []
        for _, row in df.iterrows():
            try:
                discount = row.get('discount', 0)
                if pd.isna(discount):
                    discount = 0
                orders.append(Order(
                    user=user,
                    order_id=str(row['order_id']).strip(),
                    order_date=pd.to_datetime(row['order_date']),
                    customer_email=str(row.get('customer_email', '')).strip(),
                    currency=str(row['currency']).strip().upper(),
                    gross_amount=Decimal(str(row['gross_amount'])),
                    discount=Decimal(str(discount)),
                    net_amount=Decimal(str(row['net_amount'])),
                    status=str(row['status']).strip().lower(),
                ))
            except Exception as e:
                # Skip malformed rows
                continue

        Order.objects.bulk_create(orders, ignore_conflicts=True)
        return Response({'detail': f'Imported {len(orders)} orders'})
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_payments(request):
    file = request.FILES.get('file')
    if not file:
        return Response({'detail': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    user.payments.all().delete()

    try:
        df = pd.read_csv(file)
        required_cols = {'transaction_ref', 'processed_at', 'order_reference', 'currency', 'amount', 'fee', 'net_settled', 'type', 'status'}
        if not required_cols.issubset(set(df.columns)):
            missing = required_cols - set(df.columns)
            return Response({'detail': f'Missing columns: {missing}'}, status=status.HTTP_400_BAD_REQUEST)

        payments = []
        for _, row in df.iterrows():
            try:
                processed_at = row.get('processed_at')
                if pd.isna(processed_at) or str(processed_at).strip() == '':
                    processed_at = None
                else:
                    processed_at = pd.to_datetime(processed_at)

                order_ref = str(row.get('order_reference', '')).strip()

                payments.append(Payment(
                    user=user,
                    transaction_ref=str(row['transaction_ref']).strip(),
                    processed_at=processed_at,
                    order_reference=order_ref,
                    currency=str(row['currency']).strip().upper(),
                    amount=Decimal(str(row['amount'])),
                    fee=Decimal(str(row['fee'])),
                    net_settled=Decimal(str(row['net_settled'])),
                    type=str(row['type']).strip().lower(),
                    status=str(row['status']).strip().lower(),
                ))
            except Exception:
                continue

        Payment.objects.bulk_create(payments, ignore_conflicts=True)
        return Response({'detail': f'Imported {len(payments)} payments'})
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------
# Reconciliation engine (deterministic)
# ---------------------------------------------------------------------------

AMOUNT_TOLERANCE = Decimal('0.01')


def normalize_ref(ref):
    return str(ref).strip().upper()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def run_reconciliation(request):
    user = request.user
    user.reconciliation_results.all().delete()

    orders = list(user.orders.all())
    payments = list(user.payments.all())

    order_map = {}
    duplicate_order_ids = set()
    for o in orders:
        norm = normalize_ref(o.order_id)
        if norm in order_map:
            duplicate_order_ids.add(norm)
        else:
            order_map[norm] = o

    payment_map = {}
    for p in payments:
        norm = normalize_ref(p.order_reference)
        payment_map.setdefault(norm, []).append(p)

    results = []
    processed_payments = set()

    # 1. Duplicate orders (data quality)
    for norm_id in duplicate_order_ids:
        dupes = [o for o in orders if normalize_ref(o.order_id) == norm_id]
        for o in dupes:
            results.append(ReconciliationResult(
                user=user,
                order=o,
                discrepancy_type='data_quality',
                description=f'Duplicate order ID: {o.order_id}',
                amount_at_risk=o.net_amount,
            ))

    # 2. Match unique orders to payments
    matched_orders = set()
    for o in orders:
        norm = normalize_ref(o.order_id)
        if norm in duplicate_order_ids:
            continue
        matched_orders.add(norm)
        ps = payment_map.get(norm, [])

        if not ps:
            results.append(ReconciliationResult(
                user=user,
                order=o,
                discrepancy_type='missing_payment',
                description=f'Order {o.order_id} has no matching payment.',
                amount_at_risk=o.net_amount,
            ))
            continue

        if len(ps) > 1:
            total_paid = sum(p.amount for p in ps)
            if abs(total_paid - o.net_amount) <= AMOUNT_TOLERANCE:
                # Multiple payments that sum correctly — still flag as duplicate payments
                results.append(ReconciliationResult(
                    user=user,
                    order=o,
                    discrepancy_type='duplicate_payment',
                    description=f'Order {o.order_id} has {len(ps)} payments (total ${total_paid}).',
                    amount_at_risk=abs(total_paid - o.net_amount),
                ))
            else:
                results.append(ReconciliationResult(
                    user=user,
                    order=o,
                    discrepancy_type='duplicate_payment',
                    description=f'Order {o.order_id} has {len(ps)} payments totaling ${total_paid}, expected ${o.net_amount}.',
                    amount_at_risk=abs(total_paid - o.net_amount),
                ))
            for p in ps:
                processed_payments.add(p.id)
            continue

        p = ps[0]
        processed_payments.add(p.id)

        discrepancies = []
        amount_diff = abs(p.amount - o.net_amount)

        if o.currency != p.currency:
            discrepancies.append(f'Currency mismatch: order {o.currency}, payment {p.currency}')

        if amount_diff > AMOUNT_TOLERANCE:
            discrepancies.append(f'Amount mismatch: order ${o.net_amount}, payment ${p.amount} (diff ${amount_diff})')

        # Status / type mismatch checks
        if o.status == 'cancelled' and p.type == 'charge' and p.status == 'settled':
            discrepancies.append(f'Order is cancelled but a charge of ${p.amount} was settled.')
        if o.status == 'completed' and p.status == 'failed':
            discrepancies.append(f'Order is completed but payment failed.')
        if o.status == 'completed' and p.status == 'pending':
            discrepancies.append(f'Order is completed but payment is still pending.')

        if discrepancies:
            disc_type = 'currency_mismatch' if o.currency != p.currency else 'amount_mismatch'
            # Override if status mismatch is more relevant
            if any('cancelled' in d or 'failed' in d or 'pending' in d for d in discrepancies):
                disc_type = 'status_mismatch'

            results.append(ReconciliationResult(
                user=user,
                order=o,
                payment=p,
                discrepancy_type=disc_type,
                description=' '.join(discrepancies),
                amount_at_risk=amount_diff if amount_diff > AMOUNT_TOLERANCE else o.net_amount,
            ))
        else:
            results.append(ReconciliationResult(
                user=user,
                order=o,
                payment=p,
                discrepancy_type='fully_reconciled',
                description=f'Order {o.order_id} and payment {p.transaction_ref} match.',
                amount_at_risk=Decimal('0'),
            ))

    # 3. Orphan payments
    for p in payments:
        if p.id not in processed_payments:
            results.append(ReconciliationResult(
                user=user,
                payment=p,
                discrepancy_type='orphan_payment',
                description=f'Payment {p.transaction_ref} references {p.order_reference or "unknown"} but no matching order exists.',
                amount_at_risk=p.amount,
            ))

    ReconciliationResult.objects.bulk_create(results)

    return Response({
        'detail': f'Reconciliation complete. {len(results)} results created.',
        'total': len(results),
    })


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    user = request.user
    results = user.reconciliation_results.all()

    total_orders = user.orders.count()
    total_payments = user.payments.count()

    reconciled = results.filter(discrepancy_type='fully_reconciled')
    disputed = results.exclude(discrepancy_type='fully_reconciled')

    total_reconciled_value = sum(r.order.net_amount for r in reconciled if r.order)
    total_disputed_value = sum(r.order.net_amount for r in disputed if r.order)
    total_at_risk = sum(r.amount_at_risk for r in disputed)

    breakdown = {}
    for code, label in ReconciliationResult.DISCREPANCY_TYPES:
        count = results.filter(discrepancy_type=code).count()
        if count > 0 or code == 'fully_reconciled':
            breakdown[label] = count

    data = {
        'total_orders': total_orders,
        'total_payments': total_payments,
        'total_reconciled_value': total_reconciled_value,
        'total_disputed_value': total_disputed_value,
        'total_at_risk': total_at_risk,
        'discrepancy_breakdown': breakdown,
    }

    serializer = DashboardSummarySerializer(data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def discrepancy_list(request):
    user = request.user
    discrepancy_type = request.query_params.get('type')
    search = request.query_params.get('search')

    queryset = user.reconciliation_results.all().select_related('order', 'payment')

    if discrepancy_type:
        queryset = queryset.filter(discrepancy_type=discrepancy_type)

    if search:
        queryset = queryset.filter(
            models.Q(order__order_id__icontains=search) |
            models.Q(payment__transaction_ref__icontains=search) |
            models.Q(description__icontains=search)
        )

    page = request.query_params.get('page', 1)
    page_size = request.query_params.get('page_size', 50)
    from rest_framework.pagination import PageNumberPagination
    paginator = PageNumberPagination()
    paginator.page_size = int(page_size)
    result_page = paginator.paginate_queryset(queryset, request)
    serializer = ReconciliationResultSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


# ---------------------------------------------------------------------------
# LLM Explanation
# ---------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def explain_discrepancies(request):
    """Call LLM to explain one or more discrepancies in plain language."""
    result_ids = request.data.get('result_ids', [])
    if not result_ids:
        return Response({'detail': 'No result_ids provided'}, status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    results = user.reconciliation_results.filter(id__in=result_ids).select_related('order', 'payment')
    if not results:
        return Response({'detail': 'No results found'}, status=status.HTTP_400_BAD_REQUEST)

    # Build prompt
    lines = []
    for r in results:
        order_info = f"Order {r.order.order_id} (${r.order.net_amount} {r.order.currency}, status={r.order.status})" if r.order else "No order"
        payment_info = f"Payment {r.payment.transaction_ref} (${r.payment.amount} {r.payment.currency}, type={r.payment.type}, status={r.payment.status})" if r.payment else "No payment"
        lines.append(f"- {r.get_discrepancy_type_display()}: {order_info} | {payment_info}. Description: {r.description}")

    prompt = (
        "You are a financial operations analyst. Explain the following order-payment discrepancies "
        "in plain language that a non-technical revenue manager could understand. "
        "For each discrepancy, describe what likely happened and what action should be taken. "
        "Keep it concise (2-3 sentences per discrepancy) and practical.\n\n"
        + "\n".join(lines)
    )

    try:
        client = OpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
        )
        chat = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a concise financial operations analyst. Return structured JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=settings.LLM_TEMPERATURE,
            response_format={"type": "json_object"},
        )
        content = chat.choices[0].message.content
        parsed = json.loads(content)

        # Store explanation on first result for caching
        first = results.first()
        first.llm_explanation = json.dumps(parsed)
        first.save(update_fields=['llm_explanation'])

        return Response({"explanation": parsed})
    except Exception as e:
        return Response(
            {"detail": "LLM call failed", "error": str(e)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
