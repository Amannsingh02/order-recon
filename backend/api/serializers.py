from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Order, Payment, ReconciliationResult


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['user', 'created_at']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['user', 'created_at']


class ReconciliationResultSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    payment = PaymentSerializer(read_only=True)

    class Meta:
        model = ReconciliationResult
        fields = '__all__'
        read_only_fields = ['user', 'created_at']


class DashboardSummarySerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    total_payments = serializers.IntegerField()
    total_reconciled_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_disputed_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_at_risk = serializers.DecimalField(max_digits=12, decimal_places=2)
    discrepancy_breakdown = serializers.DictField()
