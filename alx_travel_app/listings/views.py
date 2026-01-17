from rest_framework import viewsets, filters, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Listing, Booking, Payment
from .serializers import (
    ListingSerializer, BookingSerializer, PaymentSerializer,
    PaymentInitiationSerializer, PaymentVerificationSerializer
)
from .payment_service import ChapaPaymentService, create_payment_for_booking
from .tasks import send_payment_confirmation_email


class ListingViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing property listings.

    Provides full CRUD operations:
    - list: GET /api/listings/
    - create: POST /api/listings/
    - retrieve: GET /api/listings/{id}/
    - update: PUT /api/listings/{id}/
    - partial_update: PATCH /api/listings/{id}/
    - destroy: DELETE /api/listings/{id}/

    Additional filters:
    - Search by title, description, location
    - Filter by property_type, available
    - Order by price_per_night, created_at
    """

    queryset = Listing.objects.select_related('host').all()
    serializer_class = ListingSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['property_type', 'available', 'location']
    search_fields = ['title', 'description', 'location', 'address']
    ordering_fields = ['price_per_night', 'created_at', 'bedrooms']
    ordering = ['-created_at']

    @action(detail=True, methods=['get'])
    def bookings(self, request, pk=None):
        """Get all bookings for a specific listing."""
        listing = self.get_object()
        bookings = listing.bookings.all()
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get only available listings."""
        available_listings = self.queryset.filter(available=True)
        serializer = self.get_serializer(available_listings, many=True)
        return Response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing bookings.

    Provides full CRUD operations:
    - list: GET /api/bookings/
    - create: POST /api/bookings/
    - retrieve: GET /api/bookings/{id}/
    - update: PUT /api/bookings/{id}/
    - partial_update: PATCH /api/bookings/{id}/
    - destroy: DELETE /api/bookings/{id}/

    Additional filters:
    - Filter by status, listing, guest
    - Order by check_in_date, total_price
    """

    queryset = Booking.objects.select_related('listing', 'guest').all()
    serializer_class = BookingSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'listing', 'guest']
    ordering_fields = ['check_in_date', 'check_out_date', 'total_price', 'created_at']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm a pending booking."""
        booking = self.get_object()
        if booking.status != 'pending':
            return Response(
                {'error': 'Only pending bookings can be confirmed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        booking.status = 'confirmed'
        booking.save()
        serializer = self.get_serializer(booking)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a booking."""
        booking = self.get_object()
        if booking.status in ['cancelled', 'completed']:
            return Response(
                {'error': f'Cannot cancel a {booking.status} booking.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        booking.status = 'cancelled'
        booking.save()
        serializer = self.get_serializer(booking)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_bookings(self, request):
        """Get bookings for the authenticated user (if authentication is enabled)."""
        # Note: This would work with authentication enabled
        # For now, requires guest_id parameter
        guest_id = request.query_params.get('guest_id')
        if guest_id:
            my_bookings = self.queryset.filter(guest_id=guest_id)
            serializer = self.get_serializer(my_bookings, many=True)
            return Response(serializer.data)
        return Response(
            {'error': 'guest_id parameter required'},
            status=status.HTTP_400_BAD_REQUEST
        )


class PaymentViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing payments.

    Provides operations for:
    - list: GET /api/payments/
    - retrieve: GET /api/payments/{id}/
    - initiate: POST /api/payments/initiate/
    - verify: POST /api/payments/verify/
    """

    queryset = Payment.objects.select_related('booking', 'booking__listing', 'booking__guest').all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'booking', 'booking__guest']
    ordering_fields = ['created_at', 'amount', 'status']
    ordering = ['-created_at']

    @action(detail=False, methods=['post'])
    def initiate(self, request):
        """
        Initiate a payment for a booking.

        POST /api/payments/initiate/
        Body: {
            "booking_id": 1,
            "email": "customer@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": "+251912345678",
            "return_url": "http://example.com/payment/success",
            "callback_url": "http://example.com/api/payments/callback/"
        }
        """
        serializer = PaymentInitiationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        
        # Get booking
        try:
            booking = Booking.objects.get(id=data['booking_id'])
        except Booking.DoesNotExist:
            return Response(
                {'error': 'Booking not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if booking already has a completed payment
        existing_payment = Payment.objects.filter(
            booking=booking,
            status='completed'
        ).first()
        
        if existing_payment:
            return Response(
                {'error': 'This booking already has a completed payment'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create payment and initiate with Chapa
        customer_info = {
            'email': data['email'],
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'phone_number': data.get('phone_number')
        }
        
        payment, response = create_payment_for_booking(
            booking=booking,
            customer_info=customer_info,
            callback_url=data.get('callback_url'),
            return_url=data.get('return_url')
        )

        if response['status'] == 'success':
            payment_serializer = PaymentSerializer(payment)
            return Response({
                'message': 'Payment initiated successfully',
                'payment': payment_serializer.data,
                'checkout_url': payment.checkout_url
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'error': 'Failed to initiate payment',
                'details': response.get('message')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def verify(self, request):
        """
        Verify a payment transaction.

        POST /api/payments/verify/
        Body: {
            "reference": "payment-reference-uuid"
        }
        """
        serializer = PaymentVerificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        reference = serializer.validated_data['reference']
        
        # Get payment by reference
        try:
            payment = Payment.objects.get(reference=reference)
        except Payment.DoesNotExist:
            return Response(
                {'error': 'Payment not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Verify with Chapa
        chapa_service = ChapaPaymentService()
        verification_response = chapa_service.verify_payment(reference)
        
        # Process verification response
        payment = chapa_service.process_payment_verification(payment, verification_response)

        # Send confirmation email if payment was successful
        if payment.status == 'completed':
            try:
                send_payment_confirmation_email.delay(payment.id)
            except Exception as e:
                # Log the error but don't fail the request
                print(f"Failed to queue confirmation email: {str(e)}")

        payment_serializer = PaymentSerializer(payment)
        return Response({
            'message': 'Payment verification completed',
            'payment': payment_serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def callback(self, request):
        """
        Callback endpoint for Chapa to notify payment status.

        POST /api/payments/callback/
        This endpoint is called by Chapa after payment completion.
        """
        # Extract transaction reference from callback data
        tx_ref = request.data.get('tx_ref') or request.data.get('trx_ref')
        
        if not tx_ref:
            return Response(
                {'error': 'Transaction reference not provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            payment = Payment.objects.get(reference=tx_ref)
        except Payment.DoesNotExist:
            return Response(
                {'error': 'Payment not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Verify payment status with Chapa
        chapa_service = ChapaPaymentService()
        verification_response = chapa_service.verify_payment(tx_ref)
        
        # Process verification
        payment = chapa_service.process_payment_verification(payment, verification_response)

        # Send confirmation email if successful
        if payment.status == 'completed':
            try:
                send_payment_confirmation_email.delay(payment.id)
            except Exception as e:
                print(f"Failed to queue confirmation email: {str(e)}")

        return Response({
            'message': 'Callback processed successfully',
            'status': payment.status
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get the current status of a payment."""
        payment = self.get_object()
        return Response({
            'reference': payment.reference,
            'status': payment.status,
            'amount': payment.amount,
            'currency': payment.currency,
            'created_at': payment.created_at,
            'paid_at': payment.paid_at
        })
