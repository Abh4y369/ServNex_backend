import razorpay
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.contenttypes.models import ContentType
from .models import Payment
from .serializers import RazorpayOrderSerializer, RazorpayPaymentVerificationSerializer
from hotels.models import Booking
from restaurants.models import TableReservation

client = razorpay.Client(auth=(settings.RAZR_KEY_ID, settings.RAZR_KEY_SECRET))

class CreateRazorpayOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = RazorpayOrderSerializer(data=request.data)
        if serializer.is_valid():
            amount = int(serializer.validated_data['amount'] * 100)  # Amount in paise
            booking_type = serializer.validated_data['booking_type']
            booking_id = serializer.validated_data['booking_id']

            # Create Razorpay Order
            data = {
                "amount": amount,
                "currency": "INR",
                "payment_capture": "1"
            }
            try:
                razorpay_order = client.order.create(data=data)
                
                # Link to internal model
                if booking_type == 'hotel':
                    content_type = ContentType.objects.get_for_model(Booking)
                else:
                    content_type = ContentType.objects.get_for_model(TableReservation)

                # Store pending payment in centralized table
                Payment.objects.create(
                    user=request.user,
                    amount=serializer.validated_data['amount'],
                    razorpay_order_id=razorpay_order['id'],
                    content_type=content_type,
                    object_id=booking_id,
                    status='pending'
                )

                # ALSO Update the specific booking object with the order ID
                booking_obj = None
                if booking_type == 'hotel':
                    booking_obj = Booking.objects.get(id=booking_id)
                else:
                    booking_obj = TableReservation.objects.get(id=booking_id)
                
                if booking_obj:
                    booking_obj.razorpay_order_id = razorpay_order['id']
                    booking_obj.save()

                return Response(razorpay_order, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = RazorpayPaymentVerificationSerializer(data=request.data)
        if serializer.is_valid():
            razorpay_order_id = serializer.validated_data['razorpay_order_id']
            razorpay_payment_id = serializer.validated_data['razorpay_payment_id']
            razorpay_signature = serializer.validated_data['razorpay_signature']

            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }

            try:
                # Verify Signature
                client.utility.verify_payment_signature(params_dict)
                
                # Update Payment object
                payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
                payment.razorpay_payment_id = razorpay_payment_id
                payment.razorpay_signature = razorpay_signature
                payment.status = 'success'
                payment.save()

                # Update the actual Booking/Reservation model
                booking_obj = payment.content_object
                if booking_obj:
                    # Update the payment_status field added earlier
                    if hasattr(booking_obj, 'payment_status'):
                        booking_obj.payment_status = 'paid'
                    
                    # For Hotels, we might also want to ensure status is 'confirmed'
                    if isinstance(booking_obj, Booking):
                        booking_obj.status = 'confirmed'
                        
                    booking_obj.save()

                return Response({"status": "Payment Verified Successfully"}, status=status.HTTP_200_OK)
            except razorpay.errors.SignatureVerificationError:
                payment = Payment.objects.filter(razorpay_order_id=razorpay_order_id).first()
                if payment:
                    payment.status = 'failed'
                    payment.save()
                return Response({"error": "Invalid Signature"}, status=status.HTTP_400_BAD_REQUEST)
            except Payment.DoesNotExist:
                return Response({"error": "Payment record not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
