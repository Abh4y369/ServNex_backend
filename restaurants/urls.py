from django.urls import path
from .views import *

urlpatterns = [
    # Restaurant endpoints
    path('restaurants/', RestaurantListCreateView.as_view(), name='restaurant-list-create'),
    path('restaurants/me/', RestaurantMeView.as_view()),                          # must be BEFORE <int:pk>
    path('restaurants/<int:pk>/', RestaurantDetailView.as_view(), name='restaurant-detail'),
    
    # Reservation endpoints
    path('reservations/', TableReservationListCreateView.as_view(), name='reservation-list-create'),
    path('reservations/<int:pk>/', RestaurantReservationDetailView.as_view(), name='reservation-detail'),
    path('my-reservations/', UserReservationsView.as_view(), name='user-reservations'),
    
    # Dashboard endpoints
    path('restaurant-dashboard/reservations/', RestaurantDashboardReservationsView.as_view()),
    path('restaurant-dashboard/previous-records/', RestaurantPreviousRecordsView.as_view()),

    # Review endpoints
    path('reviews/', ReviewCreateView.as_view(), name='review-create'),
    path('reviews/<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),
    path('restaurants/<int:pk>/reviews/', RestaurantReviewsView.as_view(), name='restaurant-reviews'),
]