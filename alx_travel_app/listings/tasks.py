"""
Celery tasks for handling asynchronous operations.
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Payment


@shared_task
def send_payment_confirmation_email(payment_id):
    """
    Send a confirmation email after successful payment.

    Args:
        payment_id (int): ID of the payment object
    """
    try:
        payment = Payment.objects.select_related(
            'booking',
            'booking__listing',
            'booking__guest'
        ).get(id=payment_id)

        if payment.status != 'completed':
            return f"Payment {payment_id} is not completed. Skipping email."

        booking = payment.booking
        guest = booking.guest
        listing = booking.listing

        # Prepare email content
        subject = f'Payment Confirmation - Booking #{booking.id}'
        message = f"""
Dear {payment.first_name} {payment.last_name},

Your payment has been successfully processed!

Payment Details:
- Transaction Reference: {payment.reference}
- Amount: {payment.amount} {payment.currency}
- Status: {payment.get_status_display()}
- Payment Date: {payment.paid_at.strftime('%Y-%m-%d %H:%M:%S')}

Booking Details:
- Booking ID: #{booking.id}
- Property: {listing.title}
- Location: {listing.location}
- Check-in Date: {booking.check_in_date}
- Check-out Date: {booking.check_out_date}
- Number of Guests: {booking.number_of_guests}
- Total Price: {booking.total_price} ETB

Thank you for booking with ALX Travel App!

Best regards,
ALX Travel Team
"""

        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@alxtravelapp.com',
            recipient_list=[payment.email],
            fail_silently=False,
        )

        return f"Confirmation email sent to {payment.email}"

    except Payment.DoesNotExist:
        return f"Payment {payment_id} not found"
    except Exception as e:
        return f"Failed to send email: {str(e)}"


@shared_task
def send_booking_reminder_email(booking_id, days_before=3):
    """
    Send a reminder email before check-in date.

    Args:
        booking_id (int): ID of the booking
        days_before (int): Number of days before check-in to send reminder
    """
    from .models import Booking
    from datetime import date, timedelta

    try:
        booking = Booking.objects.select_related('listing', 'guest').get(id=booking_id)

        # Check if we should send reminder
        reminder_date = booking.check_in_date - timedelta(days=days_before)
        if date.today() != reminder_date:
            return f"Not time to send reminder yet for booking {booking_id}"

        guest = booking.guest
        listing = booking.listing

        subject = f'Upcoming Stay Reminder - Booking #{booking.id}'
        message = f"""
Dear {guest.first_name} {guest.last_name},

This is a friendly reminder about your upcoming stay!

Booking Details:
- Property: {listing.title}
- Location: {listing.location}
- Check-in Date: {booking.check_in_date}
- Check-out Date: {booking.check_out_date}
- Number of Guests: {booking.number_of_guests}

We look forward to hosting you!

Best regards,
ALX Travel Team
"""

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@alxtravelapp.com',
            recipient_list=[guest.email],
            fail_silently=False,
        )

        return f"Reminder email sent for booking {booking_id}"

    except Booking.DoesNotExist:
        return f"Booking {booking_id} not found"
    except Exception as e:
        return f"Failed to send reminder: {str(e)}"
