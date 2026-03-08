from django.test import TestCase
from django.utils import timezone
from hotels.models import HotelDataModel, Room, Booking
from django.contrib.auth import get_user_model
from datetime import timedelta

User = get_user_model()

class BookingAvailabilityTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='password')
        self.hotel = HotelDataModel.objects.create(
            name="Test Hotel",
            owner=self.user,
            city="Test City",
            area="Test Area",
            description="Test Description",
            price="100",
        )
        self.room = Room.objects.create(
            hotel=self.hotel,
            room_type="Deluxe",
            price="200",
            total_rooms=5,
            amenities="Wifi"
        )

    def test_booking_saves_room_type(self):
        booking = Booking.objects.create(
            user=self.user,
            hotel=self.hotel,
            room=self.room,
            check_in=timezone.now().date(),
            check_out=timezone.now().date() + timedelta(days=2),
            number_of_guests=2,
            rooms_booked=1
        )
        self.assertEqual(booking.room_type_name, "Deluxe")

    def test_availability_logic(self):
        # Book 3 rooms of 5
        Booking.objects.create(
            user=self.user,
            hotel=self.hotel,
            room=self.room,
            check_in=timezone.now().date(),
            check_out=timezone.now().date() + timedelta(days=2),
            status='confirmed',
            rooms_booked=3
        )
        
        # Check availability via View logic simulation
        from django.db.models import Sum, Q
        check_in = timezone.now().date()
        check_out = timezone.now().date() + timedelta(days=2)
        
        filters = Q(hotel=self.hotel) & Q(status='confirmed') & Q(check_in__lt=check_out) & Q(check_out__gt=check_in)
        filters &= Q(room=self.room)
        
        overlapping_rooms = Booking.objects.filter(filters).aggregate(total=Sum('rooms_booked'))['total'] or 0
        remaining = self.room.total_rooms - overlapping_rooms
        
        self.assertEqual(remaining, 2)
