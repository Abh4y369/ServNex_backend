from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .models import RestaurantDataModel, TableReservation, Review
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import RestaurantSerializer, TableReservationSerializer,ReviewSerializer


class RestaurantListCreateView(generics.ListCreateAPIView):
    """
    GET: List all restaurants
    POST: Create a new restaurant (business owners only)
    """
    queryset = RestaurantDataModel.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Authenticated users can create, anyone can view

    def perform_create(self, serializer):
        # Automatically set the owner to the logged-in user
        serializer.save(owner=self.request.user)


class RestaurantDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific restaurant
    PUT/PATCH: Update restaurant details (owner only)
    DELETE: Delete restaurant (owner only)
    """
    queryset = RestaurantDataModel.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.AllowAny]  # Anyone can view

    def get_permissions(self):
        # Only owner can update/delete
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


class TableReservationListCreateView(generics.ListCreateAPIView):
    """
    GET: List all reservations (admin only)
    POST: Create a new reservation (authenticated users)
    """
    queryset = TableReservation.objects.all()
    serializer_class = TableReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Automatically set the user to the logged-in user
        serializer.save(user=self.request.user)


class UserReservationsView(generics.ListAPIView):
    """
    GET: List all reservations for the logged-in user
    """
    serializer_class = TableReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TableReservation.objects.filter(user=self.request.user)


class RestaurantReservationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TableReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return TableReservation.objects.filter(
            Q(user=user) | Q(restaurant__owner=user)
        )


class RestaurantMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        try:
            restaurant = RestaurantDataModel.objects.get(owner=request.user)
            serializer = RestaurantSerializer(restaurant, context={'request': request})
            return Response(serializer.data)
        except RestaurantDataModel.DoesNotExist:
            return Response({"error": "No restaurant found"}, status=404)

    def patch(self, request):
        try:
            restaurant = RestaurantDataModel.objects.get(owner=request.user)
        except RestaurantDataModel.DoesNotExist:
            return Response({"error": "No restaurant found"}, status=404)

        serializer = RestaurantSerializer(
            restaurant, data=request.data, partial=True, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class RestaurantDashboardReservationsView(APIView):
    """Active reservations only — completed ones go to Previous Records tab"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        reservations = TableReservation.objects.filter(
            restaurant__owner=request.user
        ).exclude(
            status='completed'
        ).select_related('user', 'restaurant')
        serializer = TableReservationSerializer(reservations, many=True)
        return Response(serializer.data)


class RestaurantPreviousRecordsView(APIView):
    """Completed reservations with reviews for the Previous Records tab"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        reservations = TableReservation.objects.filter(
            restaurant__owner=request.user,
            status='completed'
        ).select_related('user', 'restaurant').prefetch_related('review')
        serializer = TableReservationSerializer(reservations, many=True)
        return Response(serializer.data)


class ReviewCreateView(generics.CreateAPIView):
    """User submits a star rating + comment for their completed reservation"""
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}


class RestaurantReviewsView(generics.ListAPIView):
    """All reviews for a restaurant — used in dashboard previous records"""
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Review.objects.filter(restaurant_id=self.kwargs.get('pk'))


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET, PUT, PATCH, DELETE for a specific review"""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only edit/delete their own reviews
        return Review.objects.filter(user=self.request.user)
