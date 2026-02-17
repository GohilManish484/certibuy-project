from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.db.utils import OperationalError
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
	class Role(models.TextChoices):
		CUSTOMER = "customer", "Customer"
		SELLER = "seller", "Seller"
		INSPECTOR = "inspector", "Inspector"
		ADMIN = "admin", "Admin"

	role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
	profile_photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)

	@property
	def customer_profile_safe(self):
		try:
			return self.customer_profile
		except (CustomerProfile.DoesNotExist, OperationalError):
			return None


class Address(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="addresses")
	full_name = models.CharField(max_length=255)
	phone = models.CharField(max_length=20)
	address_line1 = models.CharField(max_length=255)
	address_line2 = models.CharField(max_length=255, blank=True)
	pincode = models.CharField(max_length=10)
	city = models.CharField(max_length=100)
	state = models.CharField(max_length=100)
	landmark = models.CharField(max_length=255, blank=True)
	is_default = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-is_default", "-updated_at"]

	def save(self, *args, **kwargs):
		if self.is_default:
			Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
		super().save(*args, **kwargs)
		if self.is_default:
			CustomerProfile.objects.filter(user=self.user).update(default_address=self)

	def __str__(self):
		return f"{self.full_name} - {self.city}"


class CustomerProfile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer_profile")
	profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)
	phone = models.CharField(max_length=20, blank=True)
	default_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name="default_for")
	is_verified = models.BooleanField(default=False)

	def __str__(self):
		return f"{self.user.username} Profile"


class WishlistItem(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist_items")
	product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="wishlisted_by")
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ("user", "product")
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.user.username} - {self.product.name}"


@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
	if created:
		CustomerProfile.objects.create(user=instance)
