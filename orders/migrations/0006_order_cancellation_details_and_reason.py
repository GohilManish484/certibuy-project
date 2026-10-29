from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_warrantyplan_order_warranty_charge_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='cancellation_details',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='cancellation_reason',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]