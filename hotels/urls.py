from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HotelViewSet, BookingViewSet, RoomViewSet, HotelGalleryViewSet
from .views import HotelDashboardView

router = DefaultRouter()
router.register(r'hotels', HotelViewSet, basename='hotels')
# [NEW] Register the bookings endpoint
# This will create routes like:
# GET /api/bookings/ (list user's bookings)
# POST /api/bookings/ (create new booking)
# GET /api/bookings/{id}/ (detail)
router.register(r'bookings', BookingViewSet, basename='bookings')
router.register(r'rooms', RoomViewSet, basename='rooms')
router.register(r'gallery', HotelGalleryViewSet, basename='gallery')

urlpatterns = [
    path('', include(router.urls)),
    path('hotel-dashboard/bookings/', HotelDashboardView.as_view(), name='hotel-dashboard-bookings'),
]