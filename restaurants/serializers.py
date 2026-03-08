import math
from django.db import models as db_models
from rest_framework import serializers
from .models import RestaurantDataModel, TableReservation,Review


class RestaurantSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    image = serializers.ImageField(required=False)
    menu_image = serializers.ImageField(required=False)
    interior_image = serializers.ImageField(required=False)

    class Meta:
        model = RestaurantDataModel
        fields = [
            'id', 'owner', 'owner_name', 'name', 'city', 'area', 'badge',
            'cuisine_type', 'price_range', 'average_cost_for_two', 'total_tables',
            'description', 'rating', 'image', 'menu_image', 'interior_image',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'owner', 'owner_name']

    def update(self, instance, validated_data):
        # Prevent deleting images if not sent
        for field in ['image', 'menu_image', 'interior_image']:
            if field not in validated_data:
                validated_data[field] = getattr(instance, field)
        return super().update(instance, validated_data)
    

class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.first_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'reservation', 'restaurant', 'user', 'user_name',
            'user_email', 'rating', 'comment', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'user', 'user_name', 'user_email', 'restaurant']

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def validate(self, data):
        reservation = data.get('reservation')
        # Only allow review if reservation is completed
        if reservation and reservation.status != 'completed':
            raise serializers.ValidationError("You can only review a completed reservation.")
        # One review per reservation (only check on creation)
        if not self.instance and reservation and Review.objects.filter(reservation=reservation).exists():
            raise serializers.ValidationError("You have already reviewed this reservation.")
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        reservation = validated_data['reservation']
        validated_data['user'] = request.user
        validated_data['restaurant'] = reservation.restaurant
        return super().create(validated_data)


class TableReservationSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    restaurant_image = serializers.ImageField(source='restaurant.image', read_only=True)
    menu_image = serializers.ImageField(source='restaurant.menu_image', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    has_review = serializers.SerializerMethodField()
    review_data = serializers.SerializerMethodField()

    class Meta:
        model = TableReservation
        fields = [
            'id', 'user', 'user_name', 'user_email', 'user_phone',
            'restaurant', 'restaurant_name', 'restaurant_image', 'menu_image',
            'reservation_date', 'reservation_time',
            'number_of_guests', 'tables_reserved', 'status', 'special_requests',
            'razorpay_order_id', 'payment_status',
            'has_review', 'review_data',
            'created_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'user', 'user_name', 'restaurant_name',
            'restaurant_image', 'menu_image', 'tables_reserved',
            'razorpay_order_id', 'payment_status',
            'has_review', 'review_data'
        ]

    def get_has_review(self, obj):
        """Returns True if this reservation already has a review"""
        return hasattr(obj, 'review')

    def get_review_data(self, obj):
        """Returns review details if exists, else None"""
        if hasattr(obj, 'review'):
            return {
                'id': obj.review.id,
                'rating': obj.review.rating,
                'comment': obj.review.comment,
                'created_at': obj.review.created_at,
            }
        return None

    def validate(self, data):
        from datetime import date

        # Check reservation date is not in the past
        if data.get('reservation_date') and data['reservation_date'] < date.today():
            raise serializers.ValidationError("Reservation date cannot be in the past.")

        # Table availability check
        # NOTE: 'completed' is intentionally excluded so those tables are freed up
        restaurant = data.get('restaurant')
        reservation_date = data.get('reservation_date')
        number_of_guests = data.get('number_of_guests', 1)
        tables_needed = math.ceil(number_of_guests / 4)

        if restaurant and reservation_date:
            qs = TableReservation.objects.filter(
                restaurant=restaurant,
                reservation_date=reservation_date,
                status__in=['Your Table Is Ready', 'Table Pending']  # completed NOT included
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)

            already_booked = qs.aggregate(
                total=db_models.Sum('tables_reserved')
            )['total'] or 0

            total_tables = restaurant.total_tables or 0
            available = total_tables - already_booked

            if tables_needed > available:
                raise serializers.ValidationError(
                    "Sorry, no tables are available for this date. Please try again after some time."
                )

        return data