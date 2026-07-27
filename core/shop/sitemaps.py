from django.contrib.sitemaps import Sitemap
from .models import ProductModel, ProductCategoryModel, ProductStatusType


class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return ProductModel.objects.filter(status=ProductStatusType.publish.value)  # فقط محصولات publish شده (بسته به مقدار enum خودت status=publish رو چک کن)

    def lastmod(self, obj):
        return obj.updated_date

    def location(self, obj):
        return f"/product/{obj.slug}/"


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return ProductCategoryModel.objects.all()

    def lastmod(self, obj):
        return obj.updated_date

    def location(self, obj):
        return f"/category/{obj.slug}/"  # اگه URL دسته‌بندیت فرق داره، مطابقش کن