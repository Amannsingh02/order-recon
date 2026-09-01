from django.contrib import admin
from .models import Order, Payment, ReconciliationResult


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'customer_email', 'net_amount', 'currency', 'status', 'order_date']
    list_filter = ['status', 'currency']
    search_fields = ['order_id', 'customer_email']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_ref', 'user', 'order_reference', 'amount', 'currency', 'type', 'status']
    list_filter = ['type', 'status', 'currency']
    search_fields = ['transaction_ref', 'order_reference']


@admin.register(ReconciliationResult)
class ReconciliationResultAdmin(admin.ModelAdmin):
    list_display = ['discrepancy_type', 'user', 'order', 'payment', 'amount_at_risk', 'created_at']
    list_filter = ['discrepancy_type']
    search_fields = ['order__order_id', 'payment__transaction_ref', 'description']
