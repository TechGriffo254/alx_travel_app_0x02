from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Listing, Booking, Payment


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class ListingSerializer(serializers.ModelSerializer):
    """Serializer for Listing model."""

    host = UserSerializer(read_only=True)
    host_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='host',
        write_only=True
    )

    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'description', 'property_type', 'price_per_night',
            'location', 'address', 'bedrooms', 'bathrooms', 'max_guests',
            'amenities', 'available', 'host', 'host_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model."""

    listing = ListingSerializer(read_only=True)
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.all(),
        source='listing',
        write_only=True
    )
    guest = UserSerializer(read_only=True)
    guest_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='guest',
        write_only=True
    )

    class Meta:
        model = Booking
        fields = [
            'id', 'listing', 'listing_id', 'guest', 'guest_id',
            'check_in_date', 'check_out_date', 'number_of_guests',
            'total_price', 'status', 'special_requests',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_price', 'created_at', 'updated_at']

    def validate(self, data):
        """Validate booking dates and guest capacity."""
        check_in = data.get('check_in_date')
        check_out = data.get('check_out_date')
        number_of_guests = data.get('number_of_guests')
        listing = data.get('listing')

        # Validate check-out is after check-in
        if check_in and check_out:
            if check_out <= check_in:
                raise serializers.ValidationError(
                    "Check-out date must be after check-in date."
                )

        # Validate guest capacity
        if listing and number_of_guests:
            if number_of_guests > listing.max_guests:
                raise serializers.ValidationError(
                    f"Number of guests exceeds maximum capacity of {listing.max_guests}."
                )

        # Validate listing availability
        if listing and not listing.available:
            raise serializers.ValidationError(
                "This listing is not currently available for booking."
            )

        return data


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model."""

    booking = BookingSerializer(read_only=True)
    booking_id = serializers.PrimaryKeyRelatedField(
        queryset=Booking.objects.all(),
        source='booking',
        write_only=True
    )

    class Meta:
        model = Payment
        fields = [
            'id', 'booking', 'booking_id', 'transaction_id', 'reference',
            'amount', 'currency', 'status', 'checkout_url', 'email',
            'first_name', 'last_name', 'phone_number', 'payment_response',
            'verification_response', 'created_at', 'updated_at', 'paid_at'
        ]
        read_only_fields = [
            'id', 'reference', 'transaction_id', 'checkout_url', 'status',
            'payment_response', 'verification_response', 'created_at',
            'updated_at', 'paid_at'
        ]

    def validate(self, data):
        """Validate payment data."""
        booking = data.get('booking')
        amount = data.get('amount')

        # Validate amount matches booking total
        if booking and amount:
            if amount != booking.total_price:
                raise serializers.ValidationError(
                    f"Payment amount must match booking total price of {booking.total_price}."
                )

        # Validate booking status
        if booking and booking.status == 'cancelled':
            raise serializers.ValidationError(
                "Cannot create payment for a cancelled booking."
            )

        return data


class PaymentInitiationSerializer(serializers.Serializer):
    """Serializer for initiating a payment."""
    
    booking_id = serializers.IntegerField()
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(max_length=20, required=False)
    return_url = serializers.URLField(required=False)
    callback_url = serializers.URLField(required=False)


class PaymentVerificationSerializer(serializers.Serializer):
    """Serializer for payment verification response."""
    
    reference = serializers.CharField(max_length=255)
