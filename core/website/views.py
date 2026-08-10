from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
)
from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import Count

from .forms import NewsLetterForm
from shop.models import (
    ProductModel,
    ProductCategoryModel,
    ProductBrandModel,
    
)
from .models import BlogModel, BlogCategoryModel


class HomeView(TemplateView):
    template_name = "website/home.html"
    
    def post(self, request, *args, **kwargs):
        form = NewsLetterForm(request.POST)
        if form.is_valid():
            messages.success(request, 'شماره تلفن شما با موفقیت ثبت شد')
            form.save()
        else:
            messages.error(request, 'شماره تلفن وارد شده معتبر نمی باشد')
        return redirect('website:home')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['four_product'] = ProductModel.objects.all().order_by('-created_date')[:4]
        context['hero_slides'] = [
            {
                "image": 'images/slider-10.png',
                "title1": "هر ایده",
                "title2": "ابزاری مخصوص خود دارد",
                "subtitle": "با بهترین لوازم هنری راهت را شروع کن و از مسیر لذت ببر...",
                "primary_url": "{% url 'shop:show-product-view' %}", 
                "primary_text": "مشاهده محصولات",
                "secondary_url": "{% url 'website:categories' %}", 
                "secondary_text": "دسته‌بندی‌ها",
            },
        ]
        return context

class AboutView(TemplateView):
    template_name = "website/about.html" 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['avtive_page'] = 'about'
        return context


class RuleQuView(TemplateView):
    template_name = 'website/rule_qu.html'
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['avtive_page'] = 'rule_qu'
        return context


class CategoriesView(ListView):
    template_name = 'website/categories.html'
    paginate_by = 8
    
    queryset = ProductCategoryModel.objects.annotate(
        product_count=Count('products')
    )

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['avtive_page'] = 'categories'
        return context
    

class BrandsView(ListView):
    template_name = 'website/brands.html'
    paginate_by = 8

    queryset = ProductBrandModel.objects.annotate(
        product_count=Count('products')
    )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['avtive_page'] = 'brands'
        return context


class BlogPostView(ListView):
    template_name = 'website/blog-post.html'
    paginate_by = 4

    def get_queryset(self):
        queryset = BlogModel.objects.all()

        if q:= self.request.GET.get("q"):
            queryset = BlogModel.objects.filter(title__contains=q)

        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['avtive_page'] = 'blog-post'
        return context


class BlogPostDetailView(DetailView):
    template_name = 'website/blog-post-detail.html'
    queryset = BlogModel.objects.select_related('category').prefetch_related('key_points', 'faqs', 'related_products')
    context_object_name = "blog"



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['avtive_page'] = 'blog-post-detail'
        context['sidebar_categories'] = BlogCategoryModel.objects.all()
        context['related_posts'] = BlogModel.objects.filter(category=self.object.category).exclude(pk=self.object.pk)[:4]
        return context

    
