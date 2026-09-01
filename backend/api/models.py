from django.db import models
from django.contrib.auth.models import User


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_id = models.CharField(max_length=50, db_index=True)
    order_date = models.DateTimeField()
    customer_email = models.CharField(max_length=255, blank=True)
    currency = models.CharField(max_length=3)
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['user', 'order_id']]

    def __str__(self):
        return f"{self.order_id} ({self.user.username})"


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    transaction_ref = models.CharField(max_length=50, db_index=True, unique=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    order_reference = models.CharField(max_length=50, blank=True, db_index=True)
    currency = models.CharField(max_length=3)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    fee = models.DecimalField(max_digits=12, decimal_places=2)
    net_settled = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_ref} ({self.user.username})"


class ReconciliationResult(models.Model):
    DISCREPANCY_TYPES = [
        ('fully_reconciled', 'Fully Reconciled'),
        ('amount_mismatch', 'Amount Mismatch'),
        ('currency_mismatch', 'Currency Mismatch'),
        ('missing_payment', 'Missing Payment'),
        ('orphan_payment', 'Orphan Payment'),
        ('duplicate_payment', 'Duplicate Payment'),
        ('status_mismatch', 'Status Mismatch'),
        ('data_quality', 'Data Quality Issue'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reconciliation_results')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True, related_name='reconciliation_results')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, blank=True, related_name='reconciliation_results')
    discrepancy_type = models.CharField(max_length=30, choices=DISCREPANCY_TYPES)
    description = models.TextField(blank=True)
    amount_at_risk = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    llm_explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.discrepancy_type} - {self.user.username}"
