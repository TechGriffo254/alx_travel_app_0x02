# ALX Travel App - Payment Integration (Milestone 4)

This project demonstrates the integration of the Chapa Payment Gateway into a Django-based travel booking application. It includes secure payment initiation, verification, and status handling for bookings with automated email notifications.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Migration](#database-migration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Payment Workflow](#payment-workflow)
- [Testing Payment Integration](#testing-payment-integration)
- [Celery Background Tasks](#celery-background-tasks)
- [Environment Variables](#environment-variables)
- [Screenshots and Logs](#screenshots-and-logs)

## Overview

This milestone (Milestone 4) focuses on integrating the **Chapa Payment Gateway** into the ALX Travel App, allowing users to make secure payments for their bookings. The implementation includes:

- Payment model to track transactions
- API endpoints for payment initiation and verification
- Integration with Chapa API for secure payment processing
- Automated email notifications using Celery
- Complete payment workflow from booking to confirmation

## Features

 **Payment Model**: Track payment transactions with detailed information
 **Payment Initiation**: Create payment requests and redirect users to Chapa checkout
 **Payment Verification**: Verify payment status with Chapa API
 **Callback Handling**: Process Chapa callbacks after payment completion
 **Email Notifications**: Send confirmation emails using Celery background tasks
 **Admin Interface**: Manage payments through Django admin
 **API Documentation**: Swagger/ReDoc documentation for all endpoints

## Technologies Used

- **Django 4.2+** - Web framework
- **Django REST Framework** - API development
- **Chapa Payment Gateway** - Payment processing
- **Celery** - Asynchronous task queue
- **Redis** - Message broker for Celery
- **SQLite** - Database (can be replaced with PostgreSQL)
- **python-dotenv** - Environment variable management
- **drf-yasg** - API documentation

## Project Structure

```
alx_travel_app/
 alx_travel_app/
    __init__.py
    settings.py          # Django settings with Chapa & Celery config
    urls.py              # Main URL configuration
    celery.py            # Celery configuration
    wsgi.py
 listings/
    models.py            # Payment, Booking, Listing models
    views.py             # Payment API views
    serializers.py       # Payment serializers
    payment_service.py   # Chapa API integration service
    tasks.py             # Celery tasks for emails
    admin.py             # Admin configuration
    urls.py              # App URL configuration
 manage.py
 requirements.txt
 .env                     # Environment variables (not committed)
 .env.example            # Environment variables template
 README.md               # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Redis (for Celery)
- Chapa API account (https://developer.chapa.co/)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd alx_travel_app_0x02/alx_travel_app
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Configuration

### Step 1: Set Up Environment Variables

Copy the .env.example file to .env:

```bash
cp .env.example .env
```

Edit .env file with your credentials:

```env
# Chapa API Configuration
CHAPA_SECRET_KEY=CHASECK_TEST-your-secret-key
CHAPA_PUBLIC_KEY=CHAPUBK_TEST-your-public-key
CHAPA_ENCRYPTION_KEY=your-encryption-key

# Django Settings
SECRET_KEY=your-django-secret-key
DEBUG=True

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Chapa API URLs
CHAPA_BASE_URL=https://api.chapa.co/v1
```

### Step 2: Install Redis

**Windows:**
Download and install Redis from https://redis.io/download or use WSL

**Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

**Mac:**
```bash
brew install redis
brew services start redis
```

## Database Migration

Run migrations to create the database tables:

```bash
python manage.py makemigrations
python manage.py migrate
```

Create a superuser for admin access:

```bash
python manage.py createsuperuser
```

## Running the Application

### Terminal 1: Start Django Development Server

```bash
python manage.py runserver
```

The API will be available at: http://127.0.0.1:8000/

### Terminal 2: Start Celery Worker

```bash
# Windows
celery -A alx_travel_app worker -l info --pool=solo

# Linux/Mac
celery -A alx_travel_app worker -l info
```

### Terminal 3: Start Redis (if not running as service)

```bash
redis-server
```

## API Endpoints

### Base URL: http://127.0.0.1:8000/api/

### Listings Endpoints

- GET /api/listings/ - List all listings
- POST /api/listings/ - Create a new listing
- GET /api/listings/{id}/ - Get listing details
- PUT /api/listings/{id}/ - Update listing
- DELETE /api/listings/{id}/ - Delete listing

### Bookings Endpoints

- GET /api/bookings/ - List all bookings
- POST /api/bookings/ - Create a new booking
- GET /api/bookings/{id}/ - Get booking details
- PUT /api/bookings/{id}/ - Update booking
- POST /api/bookings/{id}/confirm/ - Confirm a booking
- POST /api/bookings/{id}/cancel/ - Cancel a booking

### Payment Endpoints

#### 1. Initiate Payment

```
POST /api/payments/initiate/
Content-Type: application/json

{
    "booking_id": 1,
    "email": "customer@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+251912345678",
    "return_url": "http://localhost:8000/payment/success",
    "callback_url": "http://localhost:8000/api/payments/callback/"
}
```

**Response:**
```json
{
    "message": "Payment initiated successfully",
    "payment": {
        "id": 1,
        "reference": "uuid-here",
        "amount": "1500.00",
        "currency": "ETB",
        "status": "pending",
        "checkout_url": "https://checkout.chapa.co/..."
    },
    "checkout_url": "https://checkout.chapa.co/..."
}
```

#### 2. Verify Payment

```
POST /api/payments/verify/
Content-Type: application/json

{
    "reference": "payment-reference-uuid"
}
```

**Response:**
```json
{
    "message": "Payment verification completed",
    "payment": {
        "id": 1,
        "reference": "uuid-here",
        "status": "completed",
        "transaction_id": "chapa-tx-id",
        "paid_at": "2026-01-17T10:30:00Z"
    }
}
```

#### 3. Payment Callback (Chapa Webhook)

```
POST /api/payments/callback/
Content-Type: application/json

{
    "tx_ref": "payment-reference-uuid",
    "status": "success"
}
```

#### 4. Get Payment Status

```
GET /api/payments/{id}/status/
```

#### 5. List All Payments

```
GET /api/payments/
```

### API Documentation

- **Swagger UI**: http://127.0.0.1:8000/api/docs/
- **ReDoc**: http://127.0.0.1:8000/api/redoc/

## Payment Workflow

### Complete Payment Flow:

1. **Create a Booking**
   ```bash
   POST /api/bookings/
   {
       "listing_id": 1,
       "guest_id": 1,
       "check_in_date": "2026-02-01",
       "check_out_date": "2026-02-05",
       "number_of_guests": 2
   }
   ```

2. **Initiate Payment**
   ```bash
   POST /api/payments/initiate/
   {
       "booking_id": 1,
       "email": "customer@example.com",
       "first_name": "John",
       "last_name": "Doe",
       "phone_number": "+251912345678"
   }
   ```
   
   Response includes checkout_url - redirect user to this URL

3. **User Completes Payment** on Chapa checkout page

4. **Chapa Sends Callback** to /api/payments/callback/

5. **Verify Payment** (optional, as callback already verifies)
   ```bash
   POST /api/payments/verify/
   {
       "reference": "payment-reference"
   }
   ```

6. **Email Sent** - Celery sends confirmation email to customer

7. **Booking Status Updated** - Booking status changes to "confirmed"

## Testing Payment Integration

### Using Chapa Sandbox Environment

Chapa provides a test environment for payment testing:

1. **Test Card Numbers:**
   - Card Number: 5200000000000007
   - Expiry: Any future date
   - CVV: Any 3 digits

2. **Test Flow:**

```bash
# Step 1: Create test user and listing via Django admin
http://127.0.0.1:8000/admin/

# Step 2: Create a booking
curl -X POST http://127.0.0.1:8000/api/bookings/ \
  -H "Content-Type: application/json" \
  -d '{
    "listing_id": 1,
    "guest_id": 1,
    "check_in_date": "2026-02-01",
    "check_out_date": "2026-02-05",
    "number_of_guests": 2
  }'

# Step 3: Initiate payment
curl -X POST http://127.0.0.1:8000/api/payments/initiate/ \
  -H "Content-Type: application/json" \
  -d '{
    "booking_id": 1,
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "phone_number": "+251912345678"
  }'

# Step 4: Visit the checkout_url from the response
# Complete payment with test card

# Step 5: Verify payment
curl -X POST http://127.0.0.1:8000/api/payments/verify/ \
  -H "Content-Type: application/json" \
  -d '{
    "reference": "your-payment-reference"
  }'
```

### Expected Results:

1.  Payment record created with status "pending"
2.  Checkout URL generated
3.  After payment: Transaction ID received from Chapa
4.  Payment status updated to "completed"
5.  Booking status updated to "confirmed"
6.  Confirmation email sent (check console if using console backend)

## Celery Background Tasks

### Available Tasks:

1. **send_payment_confirmation_email** - Sends email after successful payment
2. **send_booking_reminder_email** - Sends reminder before check-in date

### Testing Celery:

```python
# In Django shell
python manage.py shell

from listings.tasks import send_payment_confirmation_email
result = send_payment_confirmation_email.delay(payment_id=1)
print(result.get())
```

### Monitoring Celery:

Check Celery worker terminal for task execution logs.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| CHAPA_SECRET_KEY | Chapa API secret key | Yes |
| CHAPA_PUBLIC_KEY | Chapa API public key | Yes |
| CHAPA_ENCRYPTION_KEY | Chapa encryption key | Yes |
| CHAPA_BASE_URL | Chapa API base URL | No (default: https://api.chapa.co/v1) |
| SECRET_KEY | Django secret key | Yes |
| DEBUG | Debug mode | No (default: True) |
| CELERY_BROKER_URL | Redis broker URL | No (default: redis://localhost:6379/0) |
| EMAIL_BACKEND | Email backend | No (default: console) |
| EMAIL_HOST | SMTP host | No |
| EMAIL_PORT | SMTP port | No (default: 587) |

## Screenshots and Logs

### Payment Initiation Log:

```json
{
    "timestamp": "2026-01-17T10:00:00Z",
    "action": "payment_initiated",
    "booking_id": 1,
    "reference": "abc123-uuid",
    "amount": 1500.00,
    "checkout_url": "https://checkout.chapa.co/checkout/payment/abc123"
}
```

### Payment Verification Log:

```json
{
    "timestamp": "2026-01-17T10:05:00Z",
    "action": "payment_verified",
    "reference": "abc123-uuid",
    "status": "completed",
    "transaction_id": "CHX-12345",
    "booking_status": "confirmed"
}
```

### Email Confirmation Log:

```
[2026-01-17 10:05:15] Task listings.tasks.send_payment_confirmation_email[abc-123] succeeded
Confirmation email sent to customer@example.com
```

## Troubleshooting

### Common Issues:

1. **Redis Connection Error**
   - Ensure Redis is running: edis-cli ping should return PONG
   - Check Redis URL in .env

2. **Celery Not Processing Tasks**
   - Restart Celery worker
   - Check Celery logs for errors

3. **Payment Initiation Fails**
   - Verify Chapa API credentials in .env
   - Check Chapa API status
   - Review payment_service.py logs

4. **Email Not Sent**
   - Check email backend configuration
   - Verify Celery worker is running
   - Check Django logs

## Contributing

This project is part of the ALX Software Engineering program. Contributions and improvements are welcome!

## License

This project is created for educational purposes as part of the ALX program.

## Contact

For questions or support, please contact the ALX Travel Team.

---

**Project Status**:  Milestone 4 Complete - Payment Integration Implemented

**Last Updated**: January 17, 2026
