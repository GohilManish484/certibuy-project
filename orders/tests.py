from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from .models import Order


class OrderCancellationTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(
			username='cancel-customer',
			password='test-password',
		)
		self.order = Order.objects.create(
			user=self.user,
			total_amount=499,
			payment_method='cod',
			payment_status='cod_pending',
			status='confirmed',
		)
		self.url = reverse('orders:cancel_order', args=[self.order.id])
		self.client.login(username='cancel-customer', password='test-password')

	def test_cancellation_requires_reason_and_details(self):
		response = self.client.post(self.url)

		self.order.refresh_from_db()
		self.assertEqual(response.status_code, 302)
		self.assertEqual(self.order.status, 'confirmed')

	def test_customer_can_cancel_with_reason_and_details(self):
		response = self.client.post(self.url, {
			'cancellation_reason': 'changed_mind',
			'cancellation_details': 'I no longer need this product.',
		})

		self.order.refresh_from_db()
		self.assertEqual(response.status_code, 302)
		self.assertEqual(self.order.status, 'cancelled')
		self.assertEqual(self.order.cancellation_reason, 'I changed my mind')
		self.assertEqual(self.order.cancellation_details, 'I no longer need this product.')

# Create your tests here.
