# GitHub Deployment Instructions

## Prerequisites

1. Create a new GitHub repository named lx_travel_app_0x02
2. Do NOT initialize with README, .gitignore, or license (we already have these)

## Step-by-Step Deployment

### 1. Connect to GitHub

From the project directory (lx_travel_app_0x02/alx_travel_app):

```bash
# Add GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/alx_travel_app_0x02.git

# Verify remote
git remote -v
```

### 2. Push to GitHub

```bash
# Rename branch to main (GitHub default)
git branch -M main

# Push to GitHub
git push -u origin main
```

### 3. Verify Upload

Visit: https://github.com/YOUR_USERNAME/alx_travel_app_0x02

You should see:
-  All project files
-  README.md displayed on homepage
-  3 commits in history
-  .gitignore working (no .env or venv files)

## Repository Structure on GitHub

```
alx_travel_app_0x02/
 README.md                     Comprehensive documentation
 QUICKSTART.md                Quick setup guide
 PROJECT_SUMMARY.md           Project completion summary
 SETUP.md                     Previous setup instructions
 requirements.txt             Python dependencies
 .gitignore                   Git ignore rules
 .env.example                 Environment template
 manage.py
 alx_travel_app/
    __init__.py
    settings.py              Django + Chapa + Celery config
    urls.py
    celery.py                Celery setup
    ...
 listings/
     models.py                Payment model
     views.py                 Payment endpoints
     serializers.py           Payment serializers
     payment_service.py       Chapa integration
     tasks.py                 Email tasks
     admin.py                 Admin config
     ...
```

## Important Files for Review

For ALX manual QA review, ensure reviewers check:

1. **listings/models.py** - Line 80+ (Payment model)
2. **listings/views.py** - Line 130+ (PaymentViewSet)
3. **listings/payment_service.py** - Complete file (Chapa API)
4. **listings/tasks.py** - Complete file (Email notifications)
5. **alx_travel_app/settings.py** - Lines with CHAPA, CELERY, EMAIL config
6. **README.md** - Complete documentation

## Environment Variables Setup

After cloning, users must:

1. Copy .env.example to .env
2. Add their Chapa API credentials
3. Configure email settings (optional)

**Note:** .env is in .gitignore and will NOT be pushed to GitHub (security)

## Repository Settings

### Recommended GitHub Settings:

1. **Add Description:**
   "Django travel booking app with Chapa payment gateway integration - ALX Milestone 4"

2. **Add Topics:**
   - django
   - payment-gateway
   - chapa-api
   - celery
   - rest-api
   - alx-africa

3. **Add README Badge:**
   Update README.md with:
   ```markdown
   ![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
   ![Django](https://img.shields.io/badge/django-4.2+-green.svg)
   ![Status](https://img.shields.io/badge/status-complete-success.svg)
   ```

## Submission Information

### For ALX Review Portal:

**Repository URL:**
```
https://github.com/YOUR_USERNAME/alx_travel_app_0x02
```

**Directory:**
```
alx_travel_app
```

**Key Files:**
- listings/models.py
- listings/views.py
- README.md

## Post-Deployment Checklist

-  Repository created on GitHub
-  Code pushed successfully
-  README.md visible on homepage
-  All commits present (3 commits)
-  .env file NOT visible (security)
-  Repository URL submitted to ALX
-  Manual QA review requested

## Troubleshooting

### Issue: Permission Denied

```bash
# Use HTTPS instead of SSH
git remote set-url origin https://github.com/YOUR_USERNAME/alx_travel_app_0x02.git
```

### Issue: Already Exists

```bash
# Force push (only if repository is empty)
git push -f origin main
```

### Issue: Authentication Failed

1. Use GitHub Personal Access Token
2. Settings  Developer Settings  Personal Access Tokens
3. Generate token with epo scope
4. Use token as password when pushing

## Next Steps After GitHub Push

1. Submit repository URL to ALX
2. Request Manual QA Review
3. Wait for review feedback
4. Address any requested changes
5. Complete project! 

---

**Good luck with your submission!**
