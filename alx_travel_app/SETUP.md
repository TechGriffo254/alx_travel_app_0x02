# ALX Travel App API - Setup & Testing Guide

## Quick Start

1. **Navigate to project directory**
   ```powershell
   cd c:\Users\Admin\workspaces\alx_travel_app_0x01\alx_travel_app
   ```

2. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Apply migrations**
   ```powershell
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create superuser**
   ```powershell
   python manage.py createsuperuser
   ```

5. **Run server**
   ```powershell
   python manage.py runserver
   ```

## Endpoints Summary

### Base URL
`http://127.0.0.1:8000/api/`

### Documentation
- **Swagger UI**: `http://127.0.0.1:8000/api/docs/`
- **ReDoc**: `http://127.0.0.1:8000/api/redoc/`

### Listings API

```
GET    /api/listings/                     - List all listings
POST   /api/listings/                     - Create listing
GET    /api/listings/{id}/                - Get listing
PUT    /api/listings/{id}/                - Update listing
PATCH  /api/listings/{id}/                - Partial update
DELETE /api/listings/{id}/                - Delete listing
GET    /api/listings/available/           - Available listings
GET    /api/listings/{id}/bookings/       - Listing's bookings
```

### Bookings API

```
GET    /api/bookings/                     - List all bookings
POST   /api/bookings/                     - Create booking
GET    /api/bookings/{id}/                - Get booking
PUT    /api/bookings/{id}/                - Update booking
PATCH  /api/bookings/{id}/                - Partial update
DELETE /api/bookings/{id}/                - Delete booking
POST   /api/bookings/{id}/confirm/        - Confirm booking
POST   /api/bookings/{id}/cancel/         - Cancel booking
GET    /api/bookings/my_bookings/         - User's bookings
```

## Sample Data for Testing

### Create User (via Django shell or admin)
```python
python manage.py shell
from django.contrib.auth.models import User
user = User.objects.create_user('john_host', 'john@example.com', 'password123')
guest = User.objects.create_user('jane_guest', 'jane@example.com', 'password123')
```

### Create Listing (POST /api/listings/)
```json
{
  "title": "Beachfront Paradise Villa",
  "description": "Stunning 3-bedroom villa with direct beach access",
  "property_type": "villa",
  "price_per_night": "350.00",
  "location": "Malibu, CA",
  "address": "123 Pacific Coast Highway, Malibu, CA 90265",
  "bedrooms": 3,
  "bathrooms": 3,
  "max_guests": 6,
  "amenities": "WiFi, Pool, Beach Access, BBQ, Parking",
  "available": true,
  "host_id": 1
}
```

### Create Booking (POST /api/bookings/)
```json
{
  "listing_id": 1,
  "guest_id": 2,
  "check_in_date": "2024-04-01",
  "check_out_date": "2024-04-05",
  "number_of_guests": 4,
  "special_requests": "Early check-in if possible"
}
```

## Testing Workflow

1. **Create a listing** as a host
2. **Browse available listings** with filters
3. **Create a booking** as a guest
4. **Confirm the booking**
5. **View bookings** for a listing
6. **Cancel if needed**

## Features Implemented

✅ Full CRUD operations for Listings and Bookings
✅ ModelViewSet for RESTful endpoints
✅ Swagger/OpenAPI documentation
✅ Advanced filtering and search
✅ Data validation (dates, capacity, availability)
✅ Custom actions (confirm, cancel, available)
✅ Optimized queries (select_related, prefetch_related)
✅ Pagination support
✅ Admin interface
✅ Comprehensive README

## Next Steps

- Test all endpoints using Postman or Swagger UI
- Add authentication (JWT/Token)
- Deploy to production
- Add image upload capability
- Implement rating system
