from rest_framework import serializers
from .models import Payment

class RazorpayOrderSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    booking_type = serializers.ChoiceField(choices=['hotel', 'restaurant'])
    booking_id = serializers.IntegerField()

class RazorpayPaymentVerificationSerializer(serializers.Serializer):
    razorpay_order_id = serializers.CharField()
    razorpay_payment_id = serializers.CharField()
    razorpay_signature = serializers.CharField()
