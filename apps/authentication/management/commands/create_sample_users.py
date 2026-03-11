"""
Management command to create sample users for the OverWatch courier system
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from apps.authentication.models import CustomUser, Role
from apps.branches.models import Branch
from apps.staff.models import StaffProfile
from apps.drivers.models import DriverProfile
from apps.customers.models import CustomerProfile
from utils.helpers import generate_customer_id, generate_employee_id


class Command(BaseCommand):
    help = 'Create sample users for testing the OverWatch courier system'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample users...')
        
        # Create roles if they don't exist
        self._create_roles()
        
        # Create default branch if it doesn't exist
        branch = self._create_default_branch()
        
        # Create manager
        manager = self._create_manager(branch)
        
        # Create staff members
        self._create_staff(branch)
        
        # Create drivers
        self._create_drivers(branch)
        
        # Create customers
        self._create_customers(branch)
        
        self.stdout.write(self.style.SUCCESS('\nSample users created successfully!'))
        self._print_credentials()

    def _create_roles(self):
        """Create roles if they don't exist"""
        roles_data = [
            {'id': 'manager', 'name': 'Manager'},
            {'id': 'staff', 'name': 'Staff'},
            {'id': 'driver', 'name': 'Driver'},
            {'id': 'customer', 'name': 'Customer'},
        ]
        
        for role_data in roles_data:
            Role.objects.get_or_create(
                id=role_data['id'],
                defaults={'name': role_data['name']}
            )
        
        self.stdout.write(self.style.SUCCESS('✓ Roles created'))

    def _create_default_branch(self):
        """Create a default branch if it doesn't exist"""
        branch, created = Branch.objects.get_or_create(
            name='Lagos Central Branch',
            defaults={
                'city': 'Lagos',
                'address': '123 Main Street, Lagos Island, Lagos',
                'latitude': Decimal('6.5244'),
                'longitude': Decimal('3.3792'),
                'contact_phone': '+2348012345678',
                'contact_email': 'lagos@overwatch.com',
                'manager_email': 'manager@overwatch.com',
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Default branch created'))
        else:
            self.stdout.write(self.style.SUCCESS('✓ Default branch already exists'))
        
        return branch

    def _create_manager(self, branch):
        """Create a manager user"""
        user, created = CustomUser.objects.get_or_create(
            username='manager',
            defaults={
                'email': 'manager@overwatch.com',
                'first_name': 'John',
                'last_name': 'Manager',
                'role_id': 'manager',
                'phone_number': '+2348012345001',
                'is_staff': True,
            }
        )
        
        if created:
            user.set_password('password123')
            user.save()
        
        # Create staff profile for manager
        StaffProfile.objects.get_or_create(
            user=user,
            defaults={
                'branch': branch,
                'employee_id': 'MGR001',
                'position': 'operations_manager',
                'phone_number': '+2348012345001',
                'address': '456 Manager Street, Victoria Island, Lagos',
                'hire_date': timezone.now().date() - timedelta(days=365),
            }
        )
        
        return user

    def _create_staff(self, branch):
        """Create staff members"""
        staff_data = [
            {
                'username': 'parcel_clerk',
                'email': 'clerk@overwatch.com',
                'first_name': 'Sarah',
                'last_name': 'Clerk',
                'phone_number': '+2348012345002',
                'position': 'parcel_clerk',
                'address': '789 Clerk Lane, Surulere, Lagos',
            },
            {
                'username': 'dispatcher',
                'email': 'dispatcher@overwatch.com',
                'first_name': 'Mike',
                'last_name': 'Dispatcher',
                'phone_number': '+2348012345003',
                'position': 'dispatcher',
                'address': '321 Dispatch Road, Ikeja, Lagos',
            },
        ]
        
        for staff_info in staff_data:
            user, created = CustomUser.objects.get_or_create(
                username=staff_info['username'],
                defaults={
                    'email': staff_info['email'],
                    'first_name': staff_info['first_name'],
                    'last_name': staff_info['last_name'],
                    'role_id': 'staff',
                    'phone_number': staff_info['phone_number'],
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
            
            # Create staff profile
            StaffProfile.objects.get_or_create(
                user=user,
                defaults={
                    'branch': branch,
                    'employee_id': generate_employee_id('staff'),
                    'position': staff_info['position'],
                    'phone_number': staff_info['phone_number'],
                    'address': staff_info['address'],
                    'hire_date': timezone.now().date() - timedelta(days=180),
                }
            )
        
        self.stdout.write(self.style.SUCCESS('✓ Staff members created'))

    def _create_drivers(self, branch):
        """Create driver users"""
        driver_data = [
            {
                'username': 'driver1',
                'email': 'driver1@overwatch.com',
                'first_name': 'David',
                'last_name': 'Driver',
                'phone_number': '+2348012345004',
                'vehicle_name': 'Toyota Hilux',
                'vehicle_number': 'LAG-001',
                'vehicle_type': 'van',
                'vehicle_capacity_kg': 500,
            },
            {
                'username': 'driver2',
                'email': 'driver2@overwatch.com',
                'first_name': 'Emmanuel',
                'last_name': 'Okon',
                'phone_number': '+2348012345005',
                'vehicle_name': 'Honda Motorcycle',
                'vehicle_number': 'LAG-002',
                'vehicle_type': 'motorcycle',
                'vehicle_capacity_kg': 50,
            },
            {
                'username': 'driver3',
                'email': 'driver3@overwatch.com',
                'first_name': 'Chidi',
                'last_name': 'Nwachukwu',
                'phone_number': '+2348012345006',
                'vehicle_name': 'Mercedes Sprinter',
                'vehicle_number': 'LAG-003',
                'vehicle_type': 'truck',
                'vehicle_capacity_kg': 2000,
            },
        ]
        
        for driver_info in driver_data:
            user, created = CustomUser.objects.get_or_create(
                username=driver_info['username'],
                defaults={
                    'email': driver_info['email'],
                    'first_name': driver_info['first_name'],
                    'last_name': driver_info['last_name'],
                    'role_id': 'driver',
                    'phone_number': driver_info['phone_number'],
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
            
            # Create driver profile
            DriverProfile.objects.get_or_create(
                user=user,
                defaults={
                    'branch': branch,
                    'driver_id': generate_employee_id('driver'),
                    'license_number': f"DL{driver_info['phone_number'][-6:]}",
                    'license_expiry_date': timezone.now().date() + timedelta(days=730),
                    'phone_number': driver_info['phone_number'],
                    'vehicle_name': driver_info['vehicle_name'],
                    'vehicle_number': driver_info['vehicle_number'],
                    'vehicle_type': driver_info['vehicle_type'],
                    'vehicle_capacity_kg': driver_info['vehicle_capacity_kg'],
                    'hire_date': timezone.now().date() - timedelta(days=90),
                }
            )
        
        self.stdout.write(self.style.SUCCESS('✓ Drivers created'))

    def _create_customers(self, branch):
        """Create customer users"""
        customer_data = [
            {
                'username': 'customer1',
                'email': 'customer1@example.com',
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'phone_number': '+2348012345010',
                'address': '15 Admiralty Way, Lekki Phase 1, Lagos',
                'city': 'Lagos',
                'postal_code': '10176',
            },
            {
                'username': 'customer2',
                'email': 'customer2@example.com',
                'first_name': 'Bob',
                'last_name': 'Smith',
                'phone_number': '+2348012345011',
                'address': '42 Victoria Street, Lagos Island, Lagos',
                'city': 'Lagos',
                'postal_code': '10101',
            },
            {
                'username': 'customer3',
                'email': 'customer3@example.com',
                'first_name': 'Chioma',
                'last_name': 'Adeyemi',
                'phone_number': '+2348012345012',
                'address': '78 Allen Avenue, Ikeja, Lagos',
                'city': 'Lagos',
                'postal_code': '100271',
            },
            {
                'username': 'customer4',
                'email': 'customer4@example.com',
                'first_name': 'Daniel',
                'last_name': 'Okafor',
                'phone_number': '+2348012345013',
                'address': '25 Broad Street, Lagos Island, Lagos',
                'city': 'Lagos',
                'postal_code': '10101',
            },
            {
                'username': 'customer5',
                'email': 'customer5@example.com',
                'first_name': 'Fatima',
                'last_name': 'Hassan',
                'phone_number': '+2348012345014',
                'address': '89 Ozumba Mbadiwe, Victoria Island, Lagos',
                'city': 'Lagos',
                'postal_code': '10176',
            },
        ]
        
        for customer_info in customer_data:
            user, created = CustomUser.objects.get_or_create(
                username=customer_info['username'],
                defaults={
                    'email': customer_info['email'],
                    'first_name': customer_info['first_name'],
                    'last_name': customer_info['last_name'],
                    'role_id': 'customer',
                    'phone_number': customer_info['phone_number'],
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
            
            # Create customer profile
            CustomerProfile.objects.get_or_create(
                user=user,
                defaults={
                    'customer_id': generate_customer_id(),
                    'phone_number': customer_info['phone_number'],
                    'address': customer_info['address'],
                    'city': customer_info['city'],
                    'postal_code': customer_info['postal_code'],
                    'country': 'Nigeria',
                    'preferred_branch': branch,
                }
            )
        
        self.stdout.write(self.style.SUCCESS('✓ Customers created'))

    def _print_credentials(self):
        """Print login credentials"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write('SAMPLE USER CREDENTIALS')
        self.stdout.write('='*60)
        self.stdout.write('Password for all users: password123')
        self.stdout.write('-'*60)
        
        users = [
            ('Manager', 'manager@overwatch.com', 'manager'),
            ('Staff (Parcel Clerk)', 'clerk@overwatch.com', 'parcel_clerk'),
            ('Staff (Dispatcher)', 'dispatcher@overwatch.com', 'dispatcher'),
            ('Driver 1', 'driver1@overwatch.com', 'driver1'),
            ('Driver 2', 'driver2@overwatch.com', 'driver2'),
            ('Driver 3', 'driver3@overwatch.com', 'driver3'),
            ('Customer 1', 'customer1@example.com', 'customer1'),
            ('Customer 2', 'customer2@example.com', 'customer2'),
            ('Customer 3', 'customer3@example.com', 'customer3'),
            ('Customer 4', 'customer4@example.com', 'customer4'),
            ('Customer 5', 'customer5@example.com', 'customer5'),
        ]
        
        for role, email, username in users:
            self.stdout.write(f'{role:25} | {email:30} | {username}')
        
        self.stdout.write('='*60)

