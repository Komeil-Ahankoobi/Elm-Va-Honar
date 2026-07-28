from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import ProductModel, ProductCategoryModel, ProductStatusType

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['website:home', 'website:about', 'shop:show-product-view']

    def location(self, item):
        return reverse(item)

class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return ProductCategoryModel.objects.all()

    def lastmod(self, obj):
        return obj.updated_date

class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return ProductModel.objects.filter(status=ProductStatusType.publish.value)

    def lastmod(self, obj):
        return obj.updated_date