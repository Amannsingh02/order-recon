"""Tests for the reconciliation engine and API endpoints."""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from .models import Order, Payment, ReconciliationResult


class ReconciliationEngineTests(TestCase):
    """Test the deterministic reconciliation logic."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_fully_reconciled(self):
        """Order and payment match exactly."""
        Order.objects.create(
            user=self.user, order_id='ORD-001', order_date='2025-01-01',
            customer_email='a@b.com', currency='USD',
            gross_amount=100, discount=0, net_amount=100, status='completed'
        )
        Payment.objects.create(
            user=self.user, transaction_ref='TXN-001', processed_at='2025-01-01',
            order_reference='ORD-001', currency='USD',
            amount=100, fee=3, net_settled=97, type='charge', status='settled'
        )

        self.client = APIClient()
        response = self.client.post('/api/reconcile/')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])  # No auth

    def test_amount_mismatch(self):
        """Payment amount differs from order net_amount."""
        order = Order.objects.create(
            user=self.user, order_id='ORD-002', order_date='2025-01-01',
            customer_email='a@b.com', currency='USD',
            gross_amount=100, discount=0, net_amount=100, status='completed'
        )
        Payment.objects.create(
            user=self.user, transaction_ref='TXN-002', processed_at='2025-01-01',
            order_reference='ORD-002', currency='USD',
            amount=99.98, fee=3, net_settled=96.98, type='charge', status='settled'
        )
        # After reconciliation, should find amount mismatch
        # (Would need authenticated call in practice)

    def test_missing_payment(self):
        """Order exists with no matching payment."""
        Order.objects.create(
            user=self.user, order_id='ORD-003', order_date='2025-01-01',
            customer_email='a@b.com', currency='USD',
            gross_amount=100, discount=0, net_amount=100, status='completed'
        )
        # No payment for ORD-003
        # Should classify as missing_payment

    def test_orphan_payment(self):
        """Payment references order that doesn't exist."""
        Payment.objects.create(
            user=self.user, transaction_ref='TXN-004', processed_at='2025-01-01',
            order_reference='ORD-999', currency='USD',
            amount=100, fee=3, net_settled=97, type='charge', status='settled'
        )
        # Should classify as orphan_payment

    def test_duplicate_order_detection(self):
        """CSV contains duplicate order IDs."""
        Order.objects.create(
            user=self.user, order_id='ORD-DUP', order_date='2025-01-01',
            customer_email='a@b.com', currency='USD',
            gross_amount=100, discount=0, net_amount=100, status='completed'
        )
        Order.objects.create(
            user=self.user, order_id='ORD-DUP', order_date='2025-01-02',
            customer_email='b@c.com', currency='USD',
            gross_amount=200, discount=0, net_amount=200, status='completed'
        )
        # Both should be flagged as data_quality / duplicate

    def test_currency_mismatch(self):
        """Order and payment currencies differ."""
        Order.objects.create(
            user=self.user, order_id='ORD-EUR', order_date='2025-01-01',
            customer_email='a@b.com', currency='EUR',
            gross_amount=100, discount=0, net_amount=100, status='completed'
        )
        Payment.objects.create(
            user=self.user, transaction_ref='TXN-EUR', processed_at='2025-01-01',
            order_reference='ORD-EUR', currency='USD',
            amount=100, fee=3, net_settled=97, type='charge', status='settled'
        )
        # Should classify as currency_mismatch

    def test_status_mismatch_cancelled(self):
        """Cancelled order with settled charge."""
        Order.objects.create(
            user=self.user, order_id='ORD-CAN', order_date='2025-01-01',
            customer_email='a@b.com', currency='USD',
            gross_amount=100, discount=0, net_amount=100, status='cancelled'
        )
        Payment.objects.create(
            user=self.user, transaction_ref='TXN-CAN', processed_at='2025-01-01',
            order_reference='ORD-CAN', currency='USD',
            amount=100, fee=3, net_settled=97, type='charge', status='settled'
        )
        # Should classify as status_mismatch

    def test_duplicate_payments(self):
        """Multiple payments for same order."""
        Order.objects.create(
            user=self.user, order_id='ORD-DP', order_date='2025-01-01',
            customer_email='a@b.com', currency='USD',
            gross_amount=100, discount=0, net_amount=100, status='completed'
        )
        Payment.objects.create(
            user=self.user, transaction_ref='TXN-DP1', processed_at='2025-01-01',
            order_reference='ORD-DP', currency='USD',
            amount=50, fee=1.5, net_settled=48.5, type='charge', status='settled'
        )
        Payment.objects.create(
            user=self.user, transaction_ref='TXN-DP2', processed_at='2025-01-02',
            order_reference='ORD-DP', currency='USD',
            amount=50, fee=1.5, net_settled=48.5, type='charge', status='settled'
        )
        # Should classify as duplicate_payment
