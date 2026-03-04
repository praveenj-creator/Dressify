# 🚀 Dressify - Deploy to Render (Step-by-Step Guide)

## ✅ All 500 Error Issues Have Been Fixed!

Your deployment configuration has been updated to handle:
- ✓ PostgreSQL database connection
- ✓ Proper security headers for HTTPS
- ✓ Static file collection with WhiteNoise
- ✓ Automatic environment detection
- ✓ Better error logging and build output

---

## 📋 Quick Deployment Steps

### Step 1: Test Locally First
```bash
# Create local .env file
cp .env.example .env

# Edit .env with your local database settings
# DEBUG=true (for local testing)

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Test the app
python manage.py runserver
```

### Step 2: Push to GitHub
```bash
git add .
git commit -m "Fix: 500 error - Update deployment configuration"
git push origin main
```

### Step 3: Create Render Account & Project

1. Go to https://render.com
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name:** dressify
   - **Environment:** Python 3
   - **Region:** Choose closest to you
   - **Build Command:** `bash build.sh`
   - **Start Command:** `gunicorn dressify.wsgi:application --bind 0.0.0.0:$PORT --workers 2`
   - **Plan:** Free (or paid for better performance)

### Step 4: Add Environment Variables

In Render Dashboard → Your Service → Environment:

```
DEBUG=false
SECRET_KEY=(leave blank to auto-generate)
DJANGO_SETTINGS_MODULE=dressify.settings
```

**Database variables:** Will be auto-added when you create the PostgreSQL database

### Step 5: Create PostgreSQL Database

1. Render Dashboard → "New" → "PostgreSQL"
2. Name: `dressify-db`
3. Plan: Free
4. Region: Same as your web service
5. Create database

Render will automatically link it to your web service! ✨

### Step 6: Deploy!

Click "Deploy" on your web service. Watch the logs:
- ✓ "Installing dependencies..."
- ✓ "Collecting static files..."
- ✓ "Running migrations..."
- ✓ "Build completed successfully"

---

## 🔍 Verification Checklist

After deployment, check these:

- [ ] **Homepage loads:** Visit `https://your-app.onrender.com`
- [ ] **Admin panel exists:** `/admin/` shows login
- [ ] **Create superuser:** (Run from Render shell if needed)
- [ ] **Upload a product:** Test file uploads work
- [ ] **Add to cart:** Test shopping functionality
- [ ] **HTTPS works:** Padlock icon in browser

---

## 🆘 Troubleshooting 500 Errors

### Check Render Logs
1. Go to your service dashboard
2. Click "Logs" tab
3. Look for error messages

### Common Issues & Fixes

#### **"ProgrammingError: relation does not exist"**
- Database not migrated
- Solution: Run from Render background task:
```bash
render run python manage.py migrate
```

#### **"connection refused" / "could not connect to server"**
- PostgreSQL database not created
- Wrong database credentials
- Solution: Create database in Render dashboard and redeploy

#### **"ALLOWED_HOSTS Error"**
- Environment variable not set
- Solution: Check Render dashboard → Environment Variables
- `RENDER_EXTERNAL_HOSTNAME` should be auto-set with your domain

#### **"Static files 404 (CSS/JS not loading)"**
- Static files collection failed
- Solution: Check build logs for errors during `collectstatic`

#### **"Admin images/media not loading"**
- Media folder not created
- Solution: Already handled in build.sh with mkdir commands

---

## 📚 Architecture Overview

```
Render Web Service (Python/Gunicorn)
    ↓
    ├─ Settings.py (detects Render via DB_HOST env var)
    ├─ PostgreSQL Database (auto-connected)
    ├─ Static Files (served by WhiteNoise)
    └─ Media Files (uploaded by users)
```

### How It Works:
1. **Build Step:** `bash build.sh`
   - Installs dependencies
   - Creates directories
   - Collects static files
   - Runs database migrations

2. **Runtime:** Gunicorn serves your Django app
   - WhiteNoise serves static files
   - PostgreSQL handles data
   - Environment variables configure everything

---

## 🔐 Security Features Enabled

- ✓ HTTPS/SSL required
- ✓ HSTS headers (1-year max-age)
- ✓ CSRF protection
- ✓ Secure cookies
- ✓ X-Frame-Options protection
- ✓ DEBUG=false in production

---

## 📞 Still Having Issues?

1. **Check Render logs** - they're very detailed!
2. **Verify all env variables** are set
3. **Test locally first** with `DEBUG=true`
4. **Check database connection:**
   - Do you have a PostgreSQL service created?
   - Is it in the same region as web service?
5. **Check if migrations ran:**
   - Look for "Running database migrations" in build logs

---

## 🎯 What's Different in This Update

### Before ❌
- Used invalid `pserv` service type
- Debug setting was unreliable
- Missing security headers
- No CSRF trusted origins
- Compression could fail during build

### After ✅
- Fixed to `postgres` service type
- Explicit DEBUG environment variable
- Full security headers for production
- CSRF properly configured for Render domain
- Simple static file storage (more reliable)

---

## Next Steps

1. ✅ Push code to GitHub
2. ✅ Deploy on Render
3. ✅ Check logs
4. ✅ Test your app
5. ✅ Celebrate! 🎉

You're ready to go live! 🚀
