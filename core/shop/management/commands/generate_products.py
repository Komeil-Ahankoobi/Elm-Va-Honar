import random
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from faker import Faker
from pathlib import Path
from django.core.files import File

from shop.models import (
    ProductModel,
    ProductCategoryModel,
    ProductBrandModel,
    ProductStatusType,
)

BASE_DIR = Path(__file__).resolve().parent


class Command(BaseCommand):
    help = 'Generate fake products'

    def handle(self, *args, **options):
        fake = Faker(locale="fa_IR")
        image_list = [
            "./images/product.png",
        ]

        categories = list(ProductCategoryModel.objects.all())
        brands = list(ProductBrandModel.objects.all())

        for _ in range(10):  # Generate 10 fake products
            num_categories = random.randint(1, min(4, len(categories)))
            selected_categoreis = random.sample(categories, num_categories)
            selected_brand = random.choice(brands)

            title = ' '.join([fake.word() for _ in range(1, 3)])
            slug = slugify(title, allow_unicode=True)
            selected_image = image_list[0]
            image_obj = File(file=open(BASE_DIR / selected_image, "rb"), name=Path(selected_image).name)
            description = fake.paragraph(nb_sentences=10)
            brief_description = fake.paragraph(nb_sentences=1)
            stock = fake.random_int(min=0, max=10)
            status = random.choice(ProductStatusType.choices)[0]
            price = fake.random_int(min=10000, max=100000)
            discount_percent = fake.random_int(min=0, max=50)

            product = ProductModel.objects.create(
                title=title,
                slug=slug,
                image=image_obj,
                brand=selected_brand,
                description=description,
                brief_description=brief_description,
                stock=stock,
                status=status,
                price=price,
                discount_percent=discount_percent,
            )
            product.category.set(selected_categoreis)

        self.stdout.write(self.style.SUCCESS('Successfully generated 10 fake products'))