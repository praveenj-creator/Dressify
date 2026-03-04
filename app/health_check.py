"""
Health check utilities for deployment diagnostics.
Provides simple endpoints to verify application health.
"""
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import connection
from django.db.utils import OperationalError
from django.core.cache import cache
from app.models import Category

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def health_check(request):
    """
    Simple health check endpoint.
    Returns 200 if app is running, 500 if there are critical issues.
    Useful for monitoring and debugging deployment.
    """
    try:
        # Check database
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        
        # Check if migrations are applied
        Category.objects.count()
        
        return JsonResponse({
            'status': 'healthy',
            'message': 'Application is running normally',
            'checks': {
                'database': 'connected',
                'migrations': 'applied',
            }
        }, status=200)
    
    except OperationalError as e:
        logger.error(f'Health check failed - Database error: {e}')
        return JsonResponse({
            'status': 'unhealthy',
            'error': 'Database connection failed',
            'message': str(e),
        }, status=500)
    
    except Exception as e:
        logger.error(f'Health check failed: {e}')
        return JsonResponse({
            'status': 'unhealthy',
            'error': 'Unexpected error',
            'message': str(e),
        }, status=500)


@require_http_methods(["GET"])
def detailed_health_check(request):
    """
    Detailed health check with more diagnostic information.
    Use this for debugging deployment issues.
    """
    results = {
        'status': 'checking',
        'checks': {}
    }
    
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        results['checks']['database'] = {'status': 'ok', 'message': 'Connected'}
    except OperationalError as e:
        results['checks']['database'] = {'status': 'error', 'message': str(e)}
        results['status'] = 'unhealthy'
    
    # Check migrations
    try:
        category_count = Category.objects.count()
        results['checks']['migrations'] = {
            'status': 'ok',
            'message': f'Applied (Categories table accessible, {category_count} records)'
        }
    except Exception as e:
        results['checks']['migrations'] = {'status': 'error', 'message': str(e)}
        results['status'] = 'unhealthy'
    
    # Check cache
    try:
        cache.set('_health_check', 'ok', 60)
        value = cache.get('_health_check')
        cache.delete('_health_check')
        
        if value == 'ok':
            results['checks']['cache'] = {'status': 'ok', 'message': 'Working normally'}
        else:
            results['checks']['cache'] = {'status': 'warning', 'message': 'Not storing values correctly'}
    except Exception as e:
        results['checks']['cache'] = {'status': 'error', 'message': str(e)}
    
    # Set overall status
    if results['status'] != 'unhealthy':
        results['status'] = 'healthy'
    
    status_code = 200 if results['status'] == 'healthy' else 500
    return JsonResponse(results, status=status_code)
