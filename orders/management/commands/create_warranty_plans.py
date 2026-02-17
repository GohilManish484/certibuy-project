from django.core.management.base import BaseCommand
from orders.models import WarrantyPlan


class Command(BaseCommand):
    help = 'Create default warranty plans'

    def handle(self, *args, **kwargs):
        # Clear existing plans
        WarrantyPlan.objects.all().delete()
        
        # Plan 1: Extended 6 Months
        WarrantyPlan.objects.create(
            name='Extended Warranty +6 Months',
            duration_months=6,
            price=49.99,
            coverage_details=[
                'Additional 6 months coverage beyond standard warranty',
                'Hardware defect coverage',
                'Free repair or replacement',
                'Priority customer support',
                'Coverage for manufacturing defects'
            ],
            accidental_damage_covered=False,
            is_active=True,
            display_order=1
        )
        
        # Plan 2: Extended 12 Months with Accidental Damage
        WarrantyPlan.objects.create(
            name='Premium Protection +12 Months',
            duration_months=12,
            price=99.99,
            coverage_details=[
                'Full 12 months extended coverage',
                'Accidental damage protection',
                'Screen damage coverage',
                'Liquid damage protection',
                'Priority repair service',
                'Free shipping for repairs',
                '24/7 customer support'
            ],
            accidental_damage_covered=True,
            is_active=True,
            display_order=2
        )
        
        self.stdout.write(self.style.SUCCESS('Successfully created warranty plans'))
