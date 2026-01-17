"""
Service layer for handling Chapa payment gateway integration.
"""
import requests
import os
from django.conf import settings
from django.utils import timezone
from .models import Payment


class ChapaPaymentService:
    """Service class for interacting with Chapa payment gateway."""

    def __init__(self):
        self.secret_key = os.getenv('CHAPA_SECRET_KEY', settings.CHAPA_SECRET_KEY)
        self.base_url = os.getenv('CHAPA_BASE_URL', 'https://api.chapa.co/v1')
        self.headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }

    def initiate_payment(self, payment_data):
        """
        Initiate a payment transaction with Chapa.

        Args:
            payment_data (dict): Payment information including:
                - amount (float): Payment amount
                - currency (str): Currency code (default: ETB)
                - email (str): Customer email
                - first_name (str): Customer first name
                - last_name (str): Customer last name
                - tx_ref (str): Unique transaction reference
                - callback_url (str): URL for payment callback
                - return_url (str): URL to redirect after payment

        Returns:
            dict: Response from Chapa API
        """
        url = f"{self.base_url}/transaction/initialize"
        
        payload = {
            "amount": str(payment_data['amount']),
            "currency": payment_data.get('currency', 'ETB'),
            "email": payment_data['email'],
            "first_name": payment_data['first_name'],
            "last_name": payment_data['last_name'],
            "tx_ref": payment_data['tx_ref'],
            "callback_url": payment_data.get('callback_url', ''),
            "return_url": payment_data.get('return_url', ''),
            "customization": {
                "title": "ALX Travel App Booking Payment",
                "description": f"Payment for booking reference: {payment_data['tx_ref']}"
            }
        }

        # Add optional phone number if provided
        if payment_data.get('phone_number'):
            payload['phone_number'] = payment_data['phone_number']

        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
            return {
                'status': 'success',
                'data': response.json()
            }
        except requests.exceptions.RequestException as e:
            return {
                'status': 'error',
                'message': str(e),
                'data': None
            }

    def verify_payment(self, tx_ref):
        """
        Verify a payment transaction with Chapa.

        Args:
            tx_ref (str): Transaction reference to verify

        Returns:
            dict: Verification response from Chapa API
        """
        url = f"{self.base_url}/transaction/verify/{tx_ref}"

        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return {
                'status': 'success',
                'data': response.json()
            }
        except requests.exceptions.RequestException as e:
            return {
                'status': 'error',
                'message': str(e),
                'data': None
            }

    def process_payment_verification(self, payment, verification_response):
        """
        Process the verification response and update payment status.

        Args:
            payment (Payment): Payment object to update
            verification_response (dict): Response from Chapa verification API

        Returns:
            Payment: Updated payment object
        """
        if verification_response['status'] == 'success':
            data = verification_response['data']
            
            # Check if payment was successful
            if data.get('status') == 'success':
                payment.status = 'completed'
                payment.transaction_id = data.get('trx_ref')
                payment.paid_at = timezone.now()
                payment.verification_response = data
                
                # Update booking status to confirmed
                if payment.booking:
                    payment.booking.status = 'confirmed'
                    payment.booking.save()
            else:
                payment.status = 'failed'
                payment.verification_response = data
        else:
            payment.status = 'failed'
            payment.verification_response = verification_response

        payment.save()
        return payment


def create_payment_for_booking(booking, customer_info, callback_url=None, return_url=None):
    """
    Create a payment object and initiate payment with Chapa.

    Args:
        booking (Booking): Booking object to create payment for
        customer_info (dict): Customer information (email, first_name, last_name, phone_number)
        callback_url (str, optional): URL for payment callback
        return_url (str, optional): URL to redirect after payment

    Returns:
        tuple: (Payment object, payment_response dict)
    """
    # Create payment object
    payment = Payment.objects.create(
        booking=booking,
        amount=booking.total_price,
        email=customer_info['email'],
        first_name=customer_info['first_name'],
        last_name=customer_info['last_name'],
        phone_number=customer_info.get('phone_number'),
        status='pending'
    )

    # Initiate payment with Chapa
    chapa_service = ChapaPaymentService()
    payment_data = {
        'amount': float(payment.amount),
        'currency': payment.currency,
        'email': payment.email,
        'first_name': payment.first_name,
        'last_name': payment.last_name,
        'phone_number': payment.phone_number,
        'tx_ref': str(payment.reference),
        'callback_url': callback_url or '',
        'return_url': return_url or ''
    }

    response = chapa_service.initiate_payment(payment_data)

    if response['status'] == 'success' and response['data']:
        payment.checkout_url = response['data'].get('data', {}).get('checkout_url')
        payment.payment_response = response['data']
        payment.save()

    return payment, response
