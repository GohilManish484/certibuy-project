from django.db import models
from django.conf import settings


class Notification(models.Model):
	TYPE_CHOICES = [
		('order', 'Order'),
		('payment', 'Payment'),
		('refund', 'Refund'),
		('inspection', 'Inspection'),
		('system', 'System'),
		('inventory', 'Inventory'),
	]

	PRIORITY_CHOICES = [
		('low', 'Low'),
		('medium', 'Medium'),
		('high', 'High'),
	]

	CREATED_BY_CHOICES = [
		('system', 'System'),
		('admin', 'Admin'),
	]

	title = models.CharField(max_length=255)
	message = models.TextField()
	type = models.CharField(max_length=20, choices=TYPE_CHOICES)
	related_order = models.ForeignKey(
		'orders.Order',
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='admin_notifications'
	)
	priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
	is_read = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True, db_index=True)
	created_by = models.CharField(max_length=10, choices=CREATED_BY_CHOICES, default='system')

	class Meta:
		ordering = ['-created_at']
		indexes = [
			models.Index(fields=['type', 'priority']),
			models.Index(fields=['is_read', 'created_at']),
		]

	def __str__(self):
		return f"{self.get_type_display()} - {self.title}"
