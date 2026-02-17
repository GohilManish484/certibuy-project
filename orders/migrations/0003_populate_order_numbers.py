# Generated data migration to populate order_number field

from django.db import migrations
import secrets
from django.utils import timezone


def populate_order_numbers(apps, schema_editor):
    """Populate order_number for all existing orders with unique values"""
    Order = apps.get_model('orders', 'Order')
    
    for order in Order.objects.all().order_by('id'):
        if not order.order_number:  # Only if not already set
            # Generate unique order number
            order.order_number = f"ORD-{order.id:08d}-{secrets.randbelow(10000):04d}"
            order.save()


def reverse_populate(apps, schema_editor):
    """Reverse migration - clear order numbers"""
    Order = apps.get_model('orders', 'Order')
    Order.objects.all().update(order_number=None)


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_orderaddress_orderstatushistory_order_cancelled_at_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_order_numbers, reverse_populate),
    ]
