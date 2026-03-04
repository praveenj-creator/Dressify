"""
Management command to diagnose deployment issues.
Run: python manage.py check_deployment
"""
import logging
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.utils import OperationalError
from django.core.cache import cache
from app.models import User, Category, Product, Cart, Order

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Check deployment status and diagnose common issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed diagnostic information',
        )

    def handle(self, *args, **options):
        verbose = options.get('verbose', False)
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('DRESSIFY DEPLOYMENT CHECKER'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
        
        checks = [
            self.check_database,
            self.check_migrations,
            self.check_cache,
            self.check_models,
            self.check_admin_user,
            self.check_categories,
        ]
        
        passed = 0
        failed = 0
        
        for check in checks:
            try:
                result = check(verbose)
                if result:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ {check.__name__}: {str(e)}'))
                failed += 1
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(f'Results: {passed} passed, {failed} failed')
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
        
        if failed == 0:
            self.stdout.write(self.style.SUCCESS('🎉 All checks passed! Your deployment looks good.'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠️  {failed} check(s) failed. See above for details.'))

    def check_database(self, verbose=False):
        """Check database connection"""
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
            self.stdout.write(self.style.SUCCESS('✓ Database connection: OK'))
            return True
        except OperationalError as e:
            self.stdout.write(self.style.ERROR(f'✗ Database connection: FAILED - {str(e)}'))
            return False

    def check_migrations(self, verbose=False):
        """Check if migrations are applied"""
        try:
            # Try to query a model that should exist after migrations
            User.objects.count()
            self.stdout.write(self.style.SUCCESS('✓ Migrations: Applied'))
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Migrations: Not applied - {str(e)}'))
            self.stdout.write('  Run: python manage.py migrate')
            return False

    def check_cache(self, verbose=False):
        """Check cache backend"""
        try:
            cache.set('_deployment_check', 'ok', 60)
            value = cache.get('_deployment_check')
            cache.delete('_deployment_check')
            
            if value == 'ok':
                self.stdout.write(self.style.SUCCESS('✓ Cache backend: Working'))
                return True
            else:
                self.stdout.write(self.style.WARNING('⚠ Cache backend: Not storing values correctly'))
                return False
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Cache backend: FAILED - {str(e)}'))
            return False

    def check_models(self, verbose=False):
        """Check if models are accessible"""
        try:
            models_count = {
                'Users': User.objects.count(),
                'Categories': Category.objects.count(),
                'Products': Product.objects.count(),
                'Carts': Cart.objects.count(),
                'Orders': Order.objects.count(),
            }
            
            self.stdout.write(self.style.SUCCESS('✓ Models: Accessible'))
            if verbose:
                for model_name, count in models_count.items():
                    self.stdout.write(f'  - {model_name}: {count}')
            
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Models: Not accessible - {str(e)}'))
            return False

    def check_admin_user(self, verbose=False):
        """Check if admin user exists"""
        try:
            if User.objects.filter(role='admin').exists():
                admin_count = User.objects.filter(role='admin').count()
                self.stdout.write(self.style.SUCCESS(f'✓ Admin user: Exists ({admin_count} admin(s))'))
                return True
            else:
                self.stdout.write(self.style.WARNING('⚠ Admin user: Not found'))
                self.stdout.write('  Run: python manage.py createsuperuser')
                return False
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Admin user: Error - {str(e)}'))
            return False

    def check_categories(self, verbose=False):
        """Check if categories exist"""
        try:
            count = Category.objects.count()
            if count > 0:
                self.stdout.write(self.style.SUCCESS(f'✓ Categories: Found ({count} categories)'))
                if verbose:
                    for cat in Category.objects.all()[:5]:
                        self.stdout.write(f'  - {cat.name}')
                return True
            else:
                self.stdout.write(self.style.WARNING('⚠ Categories: None found (you should add some from admin)'))
                return True  # Not a failure, just a warning
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Categories: Error - {str(e)}'))
            return False
