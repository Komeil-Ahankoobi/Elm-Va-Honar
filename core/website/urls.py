from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("about/", views.AboutView.as_view(), name="about"),    
    path("rule_qu/", views.RuleQuView.as_view(), name="rule_qu"),
    path("categories/", views.CategoriesView.as_view(), name="categories"),
    path("brands/", views.BrandsView.as_view(), name="brands"),
    path("blog-post/", views.BlogPostView.as_view(), name="blog-post"),
    path("blog-post/<int:pk>/detail", views.BlogPostDetailView.as_view(), name="blog-post-detail"),
]