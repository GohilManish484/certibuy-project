from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from products.models import Product, ProductImage
import requests
from io import BytesIO

class Command(BaseCommand):
    help = 'Add sample electronic products with images'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # Sample electronic products data
        products_data = [
            {
                'name': 'MacBook Pro 16" M3 Max',
                'category': 'Electronics',
                'price': 3499.99,
                'condition': 'new',
                'description': 'Latest generation MacBook Pro with M3 Max chip, 36GB unified memory, 1TB SSD. Exceptional performance for professionals.',
                'warranty': '12 months Apple Care included',
                'image_url': 'https://via.placeholder.com/500x500?text=MacBook+Pro'
            },
            {
                'name': 'iPhone 15 Pro Max',
                'category': 'Electronics',
                'price': 1299.99,
                'condition': 'excellent',
                'description': 'Apple iPhone 15 Pro Max with Titanium design, A17 Pro chip, Pro camera system, and Dynamic Island.',
                'warranty': '6 months warranty included',
                'image_url': 'https://via.placeholder.com/500x500?text=iPhone+15+Pro'
            },
            {
                'name': 'Sony WH-1000XM5 Headphones',
                'category': 'Electronics',
                'price': 399.99,
                'condition': 'excellent',
                'description': 'Premium noise-cancelling wireless headphones with industry-leading sound quality and 8-hour battery life.',
                'warranty': '2 years manufacturer warranty',
                'image_url': 'https://via.placeholder.com/500x500?text=Sony+Headphones'
            },
            {
                'name': 'iPad Pro 12.9" 2024',
                'category': 'Electronics',
                'price': 1199.99,
                'condition': 'new',
                'description': 'Advanced tablet with M4 chip, Liquid Retina XDR display, Apple Pencil Pro, and Magic Keyboard included.',
                'warranty': '12 months Apple warranty',
                'image_url': 'https://via.placeholder.com/500x500?text=iPad+Pro'
            },
            {
                'name': 'Samsung S24 Ultra',
                'category': 'Electronics',
                'price': 1399.99,
                'condition': 'excellent',
                'description': 'Flagship Android smartphone with 200MP main camera, 6.8" Dynamic AMOLED 2X display, and Snapdragon 8 Gen 3 processor.',
                'warranty': '12 months manufacturer warranty',
                'image_url': 'https://via.placeholder.com/500x500?text=Samsung+S24'
            },
            {
                'name': 'DJI Air 3S Drone',
                'category': 'Electronics',
                'price': 999.99,
                'condition': 'excellent',
                'description': 'Professional drone with 7km video transmission, 46-minute flight time, 4K camera, and intelligent flight modes.',
                'warranty': '12 months DJI Care included',
                'image_url': 'https://via.placeholder.com/500x500?text=DJI+Drone'
            },
            {
                'name': 'Dell XPS 15 Laptop',
                'category': 'Electronics',
                'price': 2299.99,
                'condition': 'good',
                'description': 'High-performance laptop with Intel Core i7, RTX 4070, 16GB RAM, FHD+ display. Excellent for creative professionals.',
                'warranty': '6 months remaining on 3-year warranty',
                'image_url': 'https://via.placeholder.com/500x500?text=Dell+XPS'
            },
            {
                'name': 'Apple Watch Ultra 2',
                'category': 'Electronics',
                'price': 799.99,
                'condition': 'excellent',
                'description': 'Premium smartwatch with titanium case, always-on display, action button, and advanced health tracking. Water-resistant to 100m.',
                'warranty': '12 months Apple warranty',
                'image_url': 'https://via.placeholder.com/500x500?text=Apple+Watch'
            },
            {
                'name': 'Sony A6700 Camera',
                'category': 'Electronics',
                'price': 1799.99,
                'condition': 'excellent',
                'description': 'Professional mirrorless camera with 26MP sensor, 4K 120p video, AI autofocus, and weather-sealed body. Includes 2 lenses.',
                'warranty': '24 months manufacturer warranty',
                'image_url': 'https://via.placeholder.com/500x500?text=Sony+Camera'
            },
            {
                'name': 'Apple AirPods Pro',
                'category': 'Electronics',
                'price': 249.99,
                'condition': 'new',
                'description': 'Premium wireless earbuds with active noise cancellation, transparency mode, spatial audio, and 6-hour battery life.',
                'warranty': '12 months apple warranty',
                'image_url': 'https://via.placeholder.com/500x500?text=AirPods+Pro'
            },
            {
                'name': 'Google Pixel 8 Pro',
                'category': 'Electronics',
                'price': 999.99,
                'condition': 'excellent',
                'description': 'Google flagship phone with Tensor G3, 50MP main camera, Gemini AI built-in, and 120Hz OLED display.',
                'warranty': '12 months manufacturer warranty',
                'image_url': 'https://via.placeholder.com/500x500?text=Google+Pixel'
            },
            {
                'name': 'Microsoft Surface Pro 9',
                'category': 'Electronics',
                'price': 1299.99,
                'condition': 'good',
                'description': '2-in-1 tablet laptop with Intel Core i5, 8GB RAM, 256GB SSD, and detachable keyboard. Great for on-the-go productivity.',
                'warranty': '6 months remaining warranty',
                'image_url': 'https://via.placeholder.com/500x500?text=Surface+Pro'
            },
        ]

        # Create products
        created_count = 0
        for product_data in products_data:
            try:
                # Check if product already exists
                if Product.objects.filter(name=product_data['name']).exists():
                    self.stdout.write(f"Product {product_data['name']} already exists, skipping...")
                    continue

                # Create product
                product = Product.objects.create(
                    name=product_data['name'],
                    category=product_data['category'],
                    price=product_data['price'],
                    condition_grade=product_data['condition'],
                    description=product_data['description'],
                    warranty_info=product_data['warranty'],
                    certification_status='certified'
                )

                # Download and create product image
                try:
                    response = requests.get(product_data['image_url'], timeout=10)
                    if response.status_code == 200:
                        image_content = ContentFile(response.content, name=f"{product.id}_main.jpg")
                        ProductImage.objects.create(
                            product=product,
                            image=image_content
                        )
                        self.stdout.write(self.style.SUCCESS(f'✓ Created product: {product.name} (with image)'))
                        created_count += 1
                    else:
                        self.stdout.write(f"Warning: Failed to download image for {product.name}")
                        self.stdout.write(self.style.SUCCESS(f'✓ Created product: {product.name} (without image)'))
                        created_count += 1
                except Exception as e:
                    self.stdout.write(f"Warning: Error downloading image for {product.name}: {str(e)}")
                    self.stdout.write(self.style.SUCCESS(f'✓ Created product: {product.name} (without image)'))
                    created_count += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error creating product {product_data["name"]}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'\n✓ Successfully created {created_count} sample electronic products!'))
        self.stdout.write(self.style.SUCCESS('✓ All products are now visible on the Shop page with Certified status!'))
