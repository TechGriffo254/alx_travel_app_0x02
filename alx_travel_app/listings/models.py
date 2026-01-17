from django.db import models
from django.contrib.auth.models import User
import uuid


class Listing(models.Model):
    """Model representing a property listing."""

    PROPERTY_TYPES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('villa', 'Villa'),
        ('cottage', 'Cottage'),
        ('condo', 'Condo'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPES)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255)
    address = models.TextField()
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    max_guests = models.IntegerField()
    amenities = models.TextField(help_text="Comma-separated list of amenities")
    available = models.BooleanField(default=True)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.location}"


class Booking(models.Model):
    """Model representing a booking for a listing."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bookings')
    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    number_of_guests = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    special_requests = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking #{self.id} - {self.listing.title} by {self.guest.username}"

    def save(self, *args, **kwargs):
        """Calculate total price based on number of nights."""
        if self.check_in_date and self.check_out_date:
            nights = (self.check_out_date - self.check_in_date).days
            if nights > 0:
                self.total_price = self.listing.price_per_night * nights
        super().save(*args, **kwargs)


class Payment(models.Model):
    """Model representing a payment transaction for a booking."""

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    # Generate unique reference for each payment
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    transaction_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    reference = models.CharField(max_length=255, unique=True, default=uuid.uuid4, editable=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='ETB')  # Ethiopian Birr
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Chapa-specific fields
    checkout_url = models.URLField(blank=True, null=True)
    
    # Additional metadata
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Payment response data
    payment_response = models.JSONField(blank=True, null=True)
    verification_response = models.JSONField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.reference} - {self.status} - {self.amount} {self.currency}"

    def save(self, *args, **kwargs):
        """Ensure reference is set before saving."""
        if not self.reference:
            self.reference = str(uuid.uuid4())
        super().save(*args, **kwargs)
