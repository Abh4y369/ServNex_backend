from django.urls import path
from .views import CreateRazorpayOrderView, VerifyPaymentView

urlpatterns = [
    path('razorpay/order/', CreateRazorpayOrderView.as_view(), name='razorpay-order'),
    path('razorpay/verify/', VerifyPaymentView.as_view(), name='razorpay-verify'),
]
