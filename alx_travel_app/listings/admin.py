from django.contrib import admin
from .models import Listing, Booking, Payment


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'property_type', 'location', 'price_per_night', 'available', 'host', 'created_at']
    list_filter = ['property_type', 'available', 'created_at']
    search_fields = ['title', 'description', 'location', 'address']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'property_type', 'host')
        }),
        ('Pricing & Availability', {
            'fields': ('price_per_night', 'available')
        }),
        ('Location', {
            'fields': ('location', 'address')
        }),
        ('Capacity', {
            'fields': ('bedrooms', 'bathrooms', 'max_guests')
        }),
        ('Amenities', {
            'fields': ('amenities',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'listing', 'guest', 'check_in_date', 'check_out_date', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'check_in_date', 'created_at']
    search_fields = ['listing__title', 'guest__username', 'guest__email']
    readonly_fields = ['total_price', 'created_at', 'updated_at']
    fieldsets = (
        ('Booking Details', {
            'fields': ('listing', 'guest', 'status')
        }),
        ('Dates & Guests', {
            'fields': ('check_in_date', 'check_out_date', 'number_of_guests')
        }),
        ('Pricing', {
            'fields': ('total_price',)
        }),
        ('Additional Information', {
            'fields': ('special_requests',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['reference', 'booking', 'amount', 'currency', 'status', 'email', 'created_at', 'paid_at']
    list_filter = ['status', 'currency', 'created_at', 'paid_at']
    search_fields = ['reference', 'transaction_id', 'email', 'booking__id']
    readonly_fields = ['reference', 'transaction_id', 'checkout_url', 'payment_response', 'verification_response', 'created_at', 'updated_at', 'paid_at']
    fieldsets = (
        ('Payment Information', {
            'fields': ('booking', 'reference', 'transaction_id', 'status')
        }),
        ('Amount & Currency', {
            'fields': ('amount', 'currency')
        }),
        ('Customer Details', {
            'fields': ('email', 'first_name', 'last_name', 'phone_number')
        }),
        ('Chapa Details', {
            'fields': ('checkout_url',)
        }),
        ('API Responses', {
            'fields': ('payment_response', 'verification_response'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'paid_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        # Payments should be created through the API only
        return False
