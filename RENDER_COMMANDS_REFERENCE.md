# 🚀 Render Deployment & Debugging Commands Reference

## Quick Links to Fix Blank Page

### If Your Site Shows Blank Page After Deployment:

1. **Test health endpoint** (immediately):
   ```bash
   curl https://your-app.onrender.com/health/
   ```

2. **Check detailed diagnostics**:
   ```bash
   curl https://your-app.onrender.com/health/detailed/
   ```

3. **View Render logs**:
   - Dashboard → Your Service → Logs tab

4. **Run local check**:
   ```bash
   python manage.py check_deployment --verbose
   ```

---

## 🔧 Render Shell Commands

Access shell: **Render Dashboard → Your Service → Shell**

### Run Diagnostic Check
```bash
python manage.py check_deployment --verbose
```

Output shows:
- ✓ Database connection status
- ✓ Migrations applied
- ✓ Cache working
- ✓ Model access
- ✓ Admin user exists
- ✓ Categories available

### Check/Fix Database

```bash
# List all migrations
python manage.py showmigrations

# Run migrations
python manage.py migrate

# Run migrations with verbose output
python manage.py migrate --verbosity 2

# Reset database (WARNING: Deletes data!)
python manage.py flush --no-input
```

### Database Debugging

```bash
# Access PostgreSQL shell
python manage.py dbshell

# Inside dbshell:
\dt                                    # List all tables
SELECT COUNT(*) FROM app_user;        # Count users
SELECT COUNT(*) FROM app_category;    # Count categories
\q                                     # Exit
```

### Create Admin User

```bash
python manage.py createsuperuser

# Or for scripted creation:
python manage.py shell
>>> from app.models import User
>>> User.objects.create_superuser('admin', 'admin@example.com', 'admin')
```

### Test Application

```bash
# Django shell
python manage.py shell

# Test models
>>> from app.models import Category, Product, User
>>> User.objects.count()
>>> Category.objects.count()
>>> Product.objects.count()

# Test database connection
>>> from django.db import connection
>>> connection.ensure_connection()
>>> print("Database OK")

# Exit
>>> exit()
```

### Collect Static Files (if needed)

```bash
# Collect static files
python manage.py collectstatic --no-input --clear

# Verbose output
python manage.py collectstatic --verbosity 2
```

### View Logs

```bash
# View Python logs
tail -f logs/app.log

# Search for errors
grep ERROR /var/log/gunicorn.log
```

---

## 🐛 Debugging Specific Issues

### **Blank Page / Forever Loading**

```bash
# 1. Check if database is accessible
python manage.py check_deployment

# 2. Test database directly
python manage.py dbshell
SELECT 1;
\q

# 3. Check context processor
python manage.py shell
>>> from app.context_processors import nav_categories
>>> from django.test import RequestFactory
>>> rf = RequestFactory()
>>> request = rf.get('/')
>>> result = nav_categories(request)
>>> print(result)
```

### **Admin Page Shows, Main Site Blank**

```bash
# Test homepage view
python manage.py shell
>>> from app.views import home
>>> print(home)

# Test if templates exist
ls -la /app/app/templates/

# Test template rendering
python manage.py template_test
```

### **Static Files Not Loading**

```bash
# Check if static files collected
python manage.py findstatic style.css

# Show static files location
python manage.py findstatic admin/css/base.css -v 0

# Re-collect
python manage.py collectstatic --no-input --clear
python manage.py collectstatic --verbosity 2
```

### **CSS/Images 404 Errors**

```bash
# Verify static files were collected
ls -la /app/staticfiles/

# Check WhiteNoise can find them
python manage.py shell
>>> from whitenoise.base import WhiteNoise
>>> print("WhiteNoise OK")

# Restart Gunicorn (if applicable)
touch /app/dressify/wsgi.py
```

---

## 📊 Monitoring & Health Checks

### API Health Check Endpoints

```bash
# Simple health check
curl -s https://your-app.onrender.com/health/ | jq

# Detailed health check  
curl -s https://your-app.onrender.com/health/detailed/ | jq

# Response format:
{
  "status": "healthy|unhealthy",
  "checks": {
    "database": "connected|error",
    "migrations": "applied|error",
    "cache": "ok|error"
  }
}
```

### Real-time Log Monitoring

```bash
# Watch logs (update continuously)
tail -f /var/log/render.log

# Search for errors
grep -i error /var/log/render.log | tail -20

# Count error occurrences  
grep -c ERROR /var/log/render.log
```

### Performance Metrics

```bash
# Check database connection pool
python manage.py shell
>>> from django.db import connection
>>> connection.get_autocommit()  # Should be True
>>> print("Connection pool OK")

# Check cache operation
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value', 60)
>>> print(cache.get('test'))
```

---

## 🔄 Deployment Workflow

### Step 1: Local Testing Before Deploy

```bash
# Run all checks locally
python manage.py check

# Run migrations locally
python manage.py migrate

# Collect static
python manage.py collectstatic --no-input

# Test server
python manage.py runserver

# Visit http://localhost:8000/health/
# Should see: {"status": "healthy", ...}
```

### Step 2: Push to GitHub

```bash
git add -A
git commit -m "Fix: Blank page - Add caching and health checks"
git push origin main
```

### Step 3: Deploy on Render

- Render Dashboard → Service → Manual Deploy (if needed)
- Wait for build: "Build completed successfully"
- Check logs for errors

### Step 4: Verify Deployment

```bash
# 1. Test health endpoint
curl https://your-app.onrender.com/health/

# 2. Visit homepage
open https://your-app.onrender.com

# 3. Test admin
open https://your-app.onrender.com/admin/

# 4. Test critical features
# - Homepage loads
# - Navigation loads
# - Admin login works
# - Can add to cart
```

---

## 🆘 Recovery Steps If Site Goes Down

### Quick Recovery

```bash
# 1. From Render Shell:
python manage.py check

# 2. If migrations needed:
python manage.py migrate

# 3. Restart service:
touch /app/dressify/wsgi.py

# 4. Verify:
curl https://your-app.onrender.com/health/
```

### Full Redeployment

```bash
# 1. From Git:
git push origin main

# 2. Render will auto-detect and redeploy
# 3. Monitor in Render Dashboard → Logs

# 4. Verify after deploy completes:
curl https://your-app.onrender.com/health/detailed/
```

---

## 📝 Environment Variables Verification

```bash
# List all environment variables
env | grep -E "DEBUG|SECRET_KEY|DB_|DJANGO"

# Expected output should show:
# DEBUG=false
# DJANGO_SETTINGS_MODULE=dressify.settings
# DB_HOST=postgres-xxxxx.onrender.com
# DB_NAME=dressify_db
# DB_USER=postgres
# DB_PASSWORD=(should be set but not visible)
# DB_PORT=5432
```

---

## 🎯 Common Command Sequences

### First Deploy Troubleshooting
```bash
# Run all checks
python manage.py check_deployment --verbose

# If migrations need attention:
python manage.py migrate --verbosity 2

# Create admin
python manage.py createsuperuser

# Verify:
python manage.py shell
>>> from app.models import User
>>> User.objects.filter(is_superuser=True).count()
```

### After Code Update
```bash
# Always run:
python manage.py migrate

# Collect static if changed:
python manage.py collectstatic --no-input

# Verify:
curl https://your-app.onrender.com/health/
```

### Database Troubleshooting
```bash
# Check connection
python manage.py dbshell
SELECT version();
\q

# Check specific table
python manage.py dbshell
SELECT COUNT(*) FROM app_user;
\q

# If empty, create user:
python manage.py createsuperuser
```

---

## ✅ Success Checklist

After deployment, verify these:

- [ ] `/health/` returns `{"status": "healthy"}`
- [ ] Homepage loads (URL: `/`)
- [ ] Admin panel loads (URL: `/admin/`)
- [ ] Can login to admin
- [ ] Can create product category
- [ ] Can add product
- [ ] Can browse products
- [ ] Can add to cart
- [ ] Navigation shows categories

If all ✅, **Deployment successful!** 🎉

---

## 📞 Support Resources

### View Detailed Trace

```bash
# Enable very verbose logging
python manage.py check_deployment --verbose

# Enable debug mode (TEMPORARY - for debugging only!)
# Change this in settings.py
DEBUG = True
# Then redeploy
# Check error messages
# Change back to DEBUG = False
```

### Export Logs

```bash
# Render logs are also visible in:
# Dashboard → Logs → Click "Export" to download
```

---

**Remember:** Most "blank page" issues are caused by:
1. ✅ Now fixed: Context processor database hang (CACHING added)
2. ✅ Now fixed: Missing connection pooling (KEEPALIVE added)
3. ✅ Now fixed: Insufficient logging (ENHANCED logging + health checks)

You should be good to go! 🚀
