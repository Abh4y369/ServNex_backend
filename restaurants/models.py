from django.db import models
from django.contrib.auth import get_user_model

# Get the user model (works with custom User models too)
User = get_user_model()

class RestaurantDataModel(models.Model):
    BADGE_CHOICES = [
        ('Fine Dining', 'Fine Dining'),
        ('Casual Dining', 'Casual Dining'),
        ('Fast Food', 'Fast Food'),
        ('Cafe', 'Cafe'),
    ]

    PRICE_RANGE_CHOICES = [
        ('₹', 'Budget-Friendly'),
        ('₹₹', 'Moderate'),
        ('₹₹₹', 'Expensive'),
        ('₹₹₹₹', 'Very Expensive'),
    ]

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='restaurants',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    badge = models.CharField(max_length=50, choices=BADGE_CHOICES, null=True, blank=True)
    cuisine_type = models.CharField(max_length=100, help_text="e.g., Italian, Chinese, Indian, Mexican", null=True, blank=True)
    price_range = models.CharField(max_length=10, choices=PRICE_RANGE_CHOICES, default='₹₹', null=True, blank=True)
    
    average_cost_for_two = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    total_tables = models.PositiveIntegerField(
        default=10, 
        help_text="Total number of tables available in the restaurant",
        null=True, blank=True
    )

    description = models.TextField()
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    
    image = models.ImageField(upload_to='restaurants/', null=True, blank=True)
    menu_image = models.ImageField(upload_to='restaurants/menus/', blank=True, null=True)
    interior_image = models.ImageField(upload_to='restaurants/interiors/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class TableReservation(models.Model):
    STATUS_CHOICES = [
        ("Table Pending", "Table Pending"),
        ("Your Table Is Ready", "Your Table Is Ready"),
        ("completed", "Completed"),
        ("cancelled", "cancelled"),
    ]

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='restaurant_reservations'
    )
    restaurant = models.ForeignKey(
        RestaurantDataModel, 
        on_delete=models.CASCADE, 
        related_name='reservations'
    )
    
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    number_of_guests = models.PositiveIntegerField(default=2)
    tables_reserved = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Table Pending')
    special_requests = models.TextField(blank=True, null=True, help_text="Any special requests or dietary restrictions")
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(
        max_length=20, 
        choices=[('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed')], 
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        import math
        self.tables_reserved = math.ceil(self.number_of_guests / 4)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.restaurant.name} on {self.reservation_date} at {self.reservation_time}"

    class Meta:
        ordering = ['-created_at']

class Review(models.Model):
    """Star rating + comment left by user after a completed reservation"""
    reservation = models.OneToOneField(
        TableReservation,
        on_delete=models.CASCADE,
        related_name='review'
    )
    restaurant = models.ForeignKey(
        RestaurantDataModel,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.PositiveSmallIntegerField(default=5, help_text="Rating from 1 to 5")
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} → {self.restaurant.name} ({self.rating}⭐)"

    class Meta:
        ordering = ['-created_at']