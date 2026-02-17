from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('orders', '0004_notificationlog_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('type', models.CharField(choices=[('order', 'Order'), ('payment', 'Payment'), ('refund', 'Refund'), ('inspection', 'Inspection'), ('system', 'System'), ('inventory', 'Inventory')], max_length=20)),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium', max_length=10)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('created_by', models.CharField(choices=[('system', 'System'), ('admin', 'Admin')], default='system', max_length=10)),
                ('related_order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='admin_notifications', to='orders.order')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['type', 'priority'], name='core_noti_type_priority_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['is_read', 'created_at'], name='core_noti_is_read_created_at_idx'),
        ),
    ]
