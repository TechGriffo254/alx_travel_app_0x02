# Quick Setup Guide

## Prerequisites
- Python 3.8+
- Git

## Quick Start (5 minutes)

### 1. Clone and Setup
```bash
cd alx_travel_app_0x02/alx_travel_app
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy .env.example to .env and update with your Chapa credentials
cp .env.example .env
```

### 3. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4. Start Services

**Terminal 1 - Django:**
```bash
python manage.py runserver
```

**Terminal 2 - Celery (Optional):**
```bash
celery -A alx_travel_app worker -l info --pool=solo
```

### 5. Access Application
- API: http://127.0.0.1:8000/api/
- Admin: http://127.0.0.1:8000/admin/
- Swagger Docs: http://127.0.0.1:8000/api/docs/

## Quick Test

1. Login to admin panel
2. Create a User
3. Create a Listing
4. Use Swagger to create a Booking
5. Use Swagger to initiate Payment
6. Visit the checkout URL

## API Quick Reference

### Create Booking
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

### Initiate Payment
```bash
POST /api/payments/initiate/
{
  "booking_id": 1,
  "email": "test@example.com",
  "first_name": "Test",
  "last_name": "User"
}
```

### Verify Payment
```bash
POST /api/payments/verify/
{
  "reference": "payment-reference-from-initiate"
}
```

## Project Files

### Core Implementation Files:
- listings/models.py - Payment, Booking, Listing models
- listings/views.py - Payment API endpoints
- listings/serializers.py - Data serializers
- listings/payment_service.py - Chapa API integration
- listings/tasks.py - Celery email tasks
- lx_travel_app/settings.py - Configuration
- lx_travel_app/celery.py - Celery setup

### Configuration Files:
- .env - Environment variables (create from .env.example)
- equirements.txt - Python dependencies
- .gitignore - Git ignore rules

## Troubleshooting

### Common Issues:

**Import Error:**
```bash
pip install -r requirements.txt
```

**Database Error:**
```bash
python manage.py migrate
```

**Celery Not Working:**
- Install Redis or run without Celery (emails will fail silently)
- Use console email backend for testing

**Payment Fails:**
- Check Chapa credentials in .env
- Verify you're using test/sandbox keys

## Support

For detailed documentation, see README.md
