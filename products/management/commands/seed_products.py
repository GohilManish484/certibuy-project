from django.core.management.base import BaseCommand
from django.db import transaction
from products.models import Product


class Command(BaseCommand):
    help = 'Seeds the database with certified refurbished products'

    def handle(self, *args, **kwargs):
        products_data = [
            {
                'name': 'iPhone 13 Pro 128GB',
                'category': 'Smartphones',
                'price': 45999.00,
                'condition_grade': 'excellent',
                'description': 'Apple iPhone 13 Pro with 128GB storage. This device has passed a 32-point quality inspection and is certified by our experts. Features A15 Bionic chip, ProMotion display, and advanced camera system.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'Samsung Galaxy S22 Ultra 256GB',
                'category': 'Smartphones',
                'price': 52999.00,
                'condition_grade': 'excellent',
                'description': 'Premium Samsung flagship with S Pen support. This device has passed a 32-point quality inspection and is certified by our experts. Includes 256GB storage, 108MP camera, and stunning AMOLED display.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'MacBook Air M1 256GB Space Gray',
                'category': 'Laptops',
                'price': 64999.00,
                'condition_grade': 'excellent',
                'description': 'Apple MacBook Air with revolutionary M1 chip. This device has passed a 32-point quality inspection and is certified by our experts. Perfect for professionals with 256GB SSD, 8GB RAM, and all-day battery life.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'Dell XPS 13 Intel i7 512GB',
                'category': 'Laptops',
                'price': 72999.00,
                'condition_grade': 'excellent',
                'description': 'Premium Dell XPS 13 ultrabook. This device has passed a 32-point quality inspection and is certified by our experts. Features 11th Gen Intel i7, 16GB RAM, 512GB SSD, and InfinityEdge display.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'Apple Watch Series 7 45mm GPS',
                'category': 'Smartwatches',
                'price': 28999.00,
                'condition_grade': 'excellent',
                'description': 'Apple Watch Series 7 with larger display. This device has passed a 32-point quality inspection and is certified by our experts. Includes health tracking, fitness monitoring, and always-on Retina display.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'Samsung Galaxy Watch 4 Classic',
                'category': 'Smartwatches',
                'price': 18999.00,
                'condition_grade': 'excellent',
                'description': 'Premium Samsung smartwatch with rotating bezel. This device has passed a 32-point quality inspection and is certified by our experts. Features body composition analysis, advanced sleep tracking, and Wear OS.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'PlayStation 5 Digital Edition',
                'category': 'Gaming Consoles',
                'price': 39999.00,
                'condition_grade': 'excellent',
                'description': 'Sony PlayStation 5 Digital Edition. This device has passed a 32-point quality inspection and is certified by our experts. Experience next-gen gaming with ultra-high-speed SSD and ray tracing.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'Xbox Series X 1TB',
                'category': 'Gaming Consoles',
                'price': 44999.00,
                'condition_grade': 'excellent',
                'description': 'Microsoft Xbox Series X with 1TB storage. This device has passed a 32-point quality inspection and is certified by our experts. Enjoy 4K gaming at 120fps with quick resume and Game Pass compatibility.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'iPad Pro 11-inch M1 128GB',
                'category': 'Tablets',
                'price': 56999.00,
                'condition_grade': 'excellent',
                'description': 'Apple iPad Pro with M1 chip and Liquid Retina display. This device has passed a 32-point quality inspection and is certified by our experts. Perfect for creative professionals with ProMotion and Apple Pencil support.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'AirPods Pro 2nd Generation',
                'category': 'Audio Accessories',
                'price': 18999.00,
                'condition_grade': 'excellent',
                'description': 'Apple AirPods Pro with active noise cancellation. This device has passed a 32-point quality inspection and is certified by our experts. Features adaptive transparency, spatial audio, and MagSafe charging.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'Sony WH-1000XM5 Headphones',
                'category': 'Audio Accessories',
                'price': 24999.00,
                'condition_grade': 'excellent',
                'description': 'Premium Sony noise-canceling headphones. This device has passed a 32-point quality inspection and is certified by our experts. Industry-leading ANC, 30-hour battery, and exceptional sound quality.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'OnePlus 10 Pro 256GB',
                'category': 'Smartphones',
                'price': 38999.00,
                'condition_grade': 'excellent',
                'description': 'OnePlus flagship with Hasselblad camera. This device has passed a 32-point quality inspection and is certified by our experts. Features Snapdragon 8 Gen 1, 120Hz AMOLED display, and 65W fast charging.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'Lenovo ThinkPad X1 Carbon Gen 9',
                'category': 'Laptops',
                'price': 84999.00,
                'condition_grade': 'excellent',
                'description': 'Business-class Lenovo ThinkPad ultrabook. This device has passed a 32-point quality inspection and is certified by our experts. Intel i7, 16GB RAM, 512GB SSD, military-grade durability.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'Nintendo Switch OLED Model',
                'category': 'Gaming Consoles',
                'price': 29999.00,
                'condition_grade': 'excellent',
                'description': 'Nintendo Switch with vibrant OLED screen. This device has passed a 32-point quality inspection and is certified by our experts. Enjoy exclusive Nintendo games with enhanced display and audio.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'Google Pixel 7 Pro 128GB',
                'category': 'Smartphones',
                'price': 42999.00,
                'condition_grade': 'excellent',
                'description': 'Google Pixel 7 Pro with exceptional camera. This device has passed a 32-point quality inspection and is certified by our experts. Features Google Tensor G2, advanced AI photography, and pure Android experience.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'Canon EOS R5 Mirrorless Camera',
                'category': 'Cameras',
                'price': 219999.00,
                'condition_grade': 'excellent',
                'description': 'Professional Canon full-frame mirrorless camera. This device has passed a 32-point quality inspection and is certified by our experts. 45MP sensor, 8K video recording, and advanced autofocus system.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'Sony A7IV Mirrorless Camera',
                'category': 'Cameras',
                'price': 189999.00,
                'condition_grade': 'excellent',
                'description': 'Premium Sony full-frame mirrorless with AI autofocus. This device has passed a 32-point quality inspection and is certified by our experts. 61MP sensor, 4K 120fps video, real-time tracking.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'DJI Air 3 Drone',
                'category': 'Drones',
                'price': 89999.00,
                'condition_grade': 'excellent',
                'description': 'Advanced DJI drone with dual cameras. This device has passed a 32-point quality inspection and is certified by our experts. 4K video, 46-minute flight time, obstacle avoidance, 60x zoom.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'DJI Mavic 3 Pro Drone',
                'category': 'Drones',
                'price': 139999.00,
                'condition_grade': 'excellent',
                'description': 'Professional DJI drone with triple cameras. This device has passed a 32-point quality inspection and is certified by our experts. 5.1K video, Cine camera, 12MP periscope lens, intelligent features.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'Samsung 65-inch 4K Smart TV',
                'category': 'Televisions',
                'price': 79999.00,
                'condition_grade': 'excellent',
                'description': 'Premium Samsung 4K QLED television. This device has passed a 32-point quality inspection and is certified by our experts. 120Hz refresh rate, Quantum processor, smart features, gaming optimization.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'LG 55-inch OLED TV',
                'category': 'Televisions',
                'price': 129999.00,
                'condition_grade': 'excellent',
                'description': 'Premium LG OLED television with perfect blacks. This device has passed a 32-point quality inspection and is certified by our experts. 4K resolution, 120Hz mode, AI upscaling, Dolby Vision.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'Sony WF-C700N Earbuds',
                'category': 'Audio Accessories',
                'price': 12999.00,
                'condition_grade': 'excellent',
                'description': 'Sony compact wireless earbuds with ANC. This device has passed a 32-point quality inspection and is certified by our experts. Noise cancellation, 8-hour battery, multipoint connection.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'Bose QuietComfort 45 Headphones',
                'category': 'Audio Accessories',
                'price': 28999.00,
                'condition_grade': 'excellent',
                'description': 'Bose premium noise-canceling headphones. This device has passed a 32-point quality inspection and is certified by our experts. Industry-leading comfort, 24-hour battery, award-winning design.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'Asus ROG Gaming Laptop RTX 3080',
                'category': 'Laptops',
                'price': 159999.00,
                'condition_grade': 'excellent',
                'description': 'High-performance gaming laptop. This device has passed a 32-point quality inspection and is certified by our experts. Intel i9, RTX 3080, 32GB RAM, 4K 144Hz display.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'MSI GE76 Raider Gaming Laptop',
                'category': 'Laptops',
                'price': 139999.00,
                'condition_grade': 'excellent',
                'description': 'Gaming workstation laptop. This device has passed a 32-point quality inspection and is certified by our experts. Intel i7, RTX 3060 Ti, 16GB RAM, 240Hz display, per-key RGB.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'Samsung Galaxy Tab S8 Ultra',
                'category': 'Tablets',
                'price': 94999.00,
                'condition_grade': 'excellent',
                'description': 'Premium Samsung tablet with S Pen. This device has passed a 32-point quality inspection and is certified by our experts. 14.6-inch display, 120Hz, Snapdragon 8 Gen 1, 12.4MP camera.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'Microsoft Surface Laptop 5',
                'category': 'Laptops',
                'price': 119999.00,
                'condition_grade': 'excellent',
                'description': 'Premium Microsoft ultrabook. This device has passed a 32-point quality inspection and is certified by our experts. Intel i5, 512GB SSD, touchscreen, Gorilla Glass display.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'GoPro Hero 11 Black',
                'category': 'Cameras',
                'price': 52999.00,
                'condition_grade': 'excellent',
                'description': 'Professional action camera. This device has passed a 32-point quality inspection and is certified by our experts. 5.3K video, waterproof, stabilization, voice control.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'Insta360 X3 360 Camera',
                'category': 'Cameras',
                'price': 79999.00,
                'condition_grade': 'excellent',
                'description': 'Professional 360-degree camera. This device has passed a 32-point quality inspection and is certified by our experts. 8K 360 video, waterproof, stabilization, editing software included.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'Amazon Echo Studio Speaker',
                'category': 'Smart Speakers',
                'price': 19999.00,
                'condition_grade': 'excellent',
                'description': 'Premium Amazon smart speaker. This device has passed a 32-point quality inspection and is certified by our experts. Spatial audio, premium drivers, Alexa integration, AirPlay support.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'Google Home Max Speaker',
                'category': 'Smart Speakers',
                'price': 24999.00,
                'condition_grade': 'excellent',
                'description': 'Google premium smart speaker. This device has passed a 32-point quality inspection and is certified by our experts. Rich sound, voice control, WiFi connectivity, Google Assist.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'Nintendo Switch Pro Handheld',
                'category': 'Gaming Consoles',
                'price': 14999.00,
                'condition_grade': 'excellent',
                'description': 'Nintendo Switch Pro handheld gaming device. This device has passed a 32-point quality inspection and is certified by our experts. 6.3-inch screen, optimized controls, TV docking.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'Oculus Quest 3 VR Headset',
                'category': 'VR Headsets',
                'price': 29999.00,
                'condition_grade': 'excellent',
                'description': 'Meta Oculus Quest 3 VR headset. This device has passed a 32-point quality inspection and is certified by our experts. Mixed reality, 4K resolution, inside-out tracking, wireless streaming.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
            {
                'name': 'Sony PlayStation VR2 Headset',
                'category': 'VR Headsets',
                'price': 64999.00,
                'condition_grade': 'excellent',
                'description': 'Premium Sony VR headset for PlayStation 5. This device has passed a 32-point quality inspection and is certified by our experts. 4K OLED, eye tracking, haptic feedback, 110° field of view.',
                'warranty_info': '6-month comprehensive warranty covering hardware defects and performance issues',
                'stock_quantity': 10,
            },
        ]

        created_count = 0
        existing_count = 0

        with transaction.atomic():
            for product_info in products_data:
                optional_fields = {}
                
                if hasattr(Product, 'is_certified'):
                    optional_fields['is_certified'] = True
                if hasattr(Product, 'certification_points'):
                    optional_fields['certification_points'] = 32
                if hasattr(Product, 'inspection_status'):
                    optional_fields['inspection_status'] = 'Passed'
                if hasattr(Product, 'is_active'):
                    optional_fields['is_active'] = True
                
                product_data = {
                    'name': product_info['name'],
                    'category': product_info['category'],
                    'price': product_info['price'],
                    'condition_grade': product_info['condition_grade'],
                    'description': product_info['description'],
                    'warranty_info': product_info['warranty_info'],
                    'stock_quantity': product_info['stock_quantity'],
                    'low_stock_threshold': 5,
                    'certification_status': 'certified',
                    'default_warranty_months': 6,
                    'is_warranty_available': True,
                }
                
                product_data.update(optional_fields)
                
                product, created = Product.objects.get_or_create(
                    name=product_info['name'],
                    defaults=product_data
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Created: {product.name}')
                    )
                else:
                    existing_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'⚠ Already exists: {product.name}')
                    )

        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Seeding complete!\n'
                f'  Created: {created_count} products\n'
                f'  Skipped: {existing_count} existing products\n'
                f'  Total: {created_count + existing_count} products\n'
            )
        )
        self.stdout.write('='*60 + '\n')
