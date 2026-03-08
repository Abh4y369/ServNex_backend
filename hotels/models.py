from django.db import models
from django.contrib.auth import get_user_model

# Get the user model (works with custom User models too)
User = get_user_model()

class HotelDataModel(models.Model):
    BADGE_CHOICES = [
        ('Luxury Stays', 'Luxury Stays'),
        ('Cheap & Best', 'Cheap & Best'),
        ('Dormitory', 'Dormitory'),
    ]

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='hotels',
        null=True,  # allow NULL temporarily if needed during migration
        blank=True
    )
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    badge = models.CharField(max_length=50, choices=BADGE_CHOICES, null=True, blank=True)
    
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    description = models.TextField()
    amenities = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='hotels/', null=True, blank=True)
    room_image1 = models.ImageField(upload_to='hotels/rooms/', blank=True, null=True)
    room_image2 = models.ImageField(upload_to='hotels/rooms/', blank=True, null=True)
    environment_image = models.ImageField(upload_to='hotels/environment/', blank=True, null=True)

    def __str__(self):
        return self.name

class Room(models.Model):
    hotel = models.ForeignKey(HotelDataModel, on_delete=models.CASCADE, related_name='rooms')
    room_type = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    adults = models.PositiveIntegerField(default=1)
    children = models.PositiveIntegerField(default=0)
    total_rooms = models.PositiveIntegerField(default=1)
    bed_type = models.CharField(max_length=50, null=True, blank=True)
    amenities = models.TextField(null=True, blank=True, help_text="Comma separated list of amenities")
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='hotels/rooms/', null=True, blank=True)

    def __str__(self):
        return f"{self.room_type} - {self.hotel.name}"

class HotelGallery(models.Model):
    hotel = models.ForeignKey(HotelDataModel, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='hotels/gallery/')

    def __str__(self):
        return f"Gallery Image for {self.hotel.name}"


# [NEW] Booking Model for handling reservations
class Booking(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='bookings'
    )
    hotel = models.ForeignKey(
        HotelDataModel, 
        on_delete=models.CASCADE, 
        related_name='bookings'
    )
    room = models.ForeignKey(
        'Room',
        on_delete=models.CASCADE,
        related_name='bookings',
        null=True,
        blank=True
    )
    
    check_in = models.DateField()
    check_out = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    number_of_guests = models.PositiveIntegerField(default=2)
    rooms_booked = models.PositiveIntegerField(default=1)
    room_type_name = models.CharField(max_length=100, null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(
        max_length=20, 
        choices=[('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed')], 
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-calculate rooms needed if not provided or too low (2 guests per room)
        import math
        min_rooms = math.ceil(self.number_of_guests / 2)
        if not self.rooms_booked or self.rooms_booked < min_rooms:
            self.rooms_booked = min_rooms
        
        if self.room and not self.room_type_name:
            self.room_type_name = self.room.room_type
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.hotel.name} ({self.rooms_booked} rooms, {self.number_of_guests} guests)"