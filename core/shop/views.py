import re
from django.db.models import Q,F, DecimalField, ExpressionWrapper
from django.db.models.functions import Round

from shop.models import ProductModel, ProductStatusType, VarientType
from shop.colors import VISTA_ACRYLIC_COLORS

from .models import (
    ProductModel, 
    ProductStatusType,
    ProductCategoryModel
)
from django.views.generic import (
    ListView,
    DetailView
)


PERSIAN_COLOR_KEYWORDS = {
    "قرمز": ["red", "scarlet", "ruby", "wine"],
    "آبی": ["blue", "cerulean", "cobalt", "turquoise", "ultramarine", "prussian", "phthalo"],
    "زرد": ["yellow", "lemon", "ochre", "naples"],
    "سبز": ["green", "viridian"],
    "بنفش": ["purple", "violet", "dioxazine"],
    "صورتی": ["pink", "magenta", "rose"],
    "قهوه‌ای": ["brown", "umber", "sienna", "bronze", "copper", "cupreous", "fuscous"],
    "مشکی": ["black", "silver", "dark"],
    "سفید": ["white", "titanium", "iridescent"],
    "نارنجی": ["orange"],
    "نقره‌ای": ["silver"],
    "طلایی": ["gold"],
    "فسفری": ["fluorescent"],
    "فلورسنت": ["fluorescent"],
    "نئون": ["fluorescent"],
    "خاکستری": ["silver"],
}


PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
ARABIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"
LATIN_DIGITS = "0123456789"

SEARCH_STOPWORDS = {
    "سایز", "شماره", "نمره", "کد",
    "رنگ", "اکریلیک", "اکرلیک", "ویستا" ,"وستا"
}

def normalize_digits(text):
    translation_table = str.maketrans(
        PERSIAN_DIGITS + ARABIC_DIGITS,
        LATIN_DIGITS + LATIN_DIGITS
    )
    return text.translate(translation_table)

def get_matching_color_codes(word):
    """اگه کلمه فارسی یا انگلیسی مربوط به یه رنگ باشه، کدهای متناظرش رو برمی‌گردونه."""
    keywords = PERSIAN_COLOR_KEYWORDS.get(word, [word.lower()])
    codes = set()
    for code, (name, hex_code) in VISTA_ACRYLIC_COLORS.items():
        name_lower = name.lower()
        for kw in keywords:
            if kw.lower() in name_lower:
                codes.add(code)
                break
    return codes

class ShopProductView(ListView):
    template_name = "shop/shop.html"
    context_object_name = "products"
    paginate_by = 6

    def get_queryset(self):
        queryset = ProductModel.objects.filter(
            status=ProductStatusType.publish.value
        ).annotate(
            final_price=Round(ExpressionWrapper(
                 F("price") - (F("price") * F("discount_percent") / 100),
                 output_field=DecimalField()
            ))
        )

        if q := self.request.GET.get('q'):
            q_normalized = normalize_digits(q)
            raw_tokens = q_normalized.split()

            numeric_tokens = [t for t in raw_tokens if t.isdigit()]
            remaining_tokens = [
                t for t in raw_tokens
                if not t.isdigit() and t not in SEARCH_STOPWORDS
            ]

            color_codes = set()
            title_tokens = []
            for token in remaining_tokens:
                matched_codes = get_matching_color_codes(token)
                if matched_codes:
                    color_codes |= matched_codes
                else:
                    title_tokens.append(token)

            search_filter = Q(title__icontains=q)

            variant_conditions = []
            if numeric_tokens:
                variant_conditions.append(
                    Q(varients__variant_type=VarientType.number, varients__number_code__in=numeric_tokens)
                )
                variant_conditions.append(
                    Q(varients__variant_type=VarientType.color, varients__color_code__in=numeric_tokens)
                )
            if color_codes:
                variant_conditions.append(
                    Q(varients__variant_type=VarientType.color, varients__color_code__in=color_codes)
                )

            if variant_conditions:
                variant_match = variant_conditions[0]
                for cond in variant_conditions[1:]:
                    variant_match |= cond

                title_match = Q()
                for word in title_tokens:
                    title_match &= Q(title__icontains=word)

                search_filter |= (title_match & variant_match)

            queryset = queryset.filter(search_filter).distinct()

        try:
            if min_price := self.request.GET.get('min_price'):
                min_price = int(min_price)
                queryset = queryset.filter(final_price__gte=min_price)
        except (ValueError, TypeError):
            pass 
        try:
            if max_price := self.request.GET.get('max_price'):
                max_price = int(max_price)
                queryset = queryset.filter(final_price__lte=max_price)
        except (ValueError, TypeError):
            pass
        
        filter_by = self.request.GET.get('filter-by')
        
        if filter_by == 'cheep_to_exp':
            queryset = queryset.order_by('final_price')        
        elif filter_by == 'exp_to_cheep':
            queryset = queryset.order_by('-final_price')        
        elif filter_by == 'new':
            queryset = queryset.order_by('-created_date')
            
        if category := self.request.GET.get('category'):
            queryset = queryset.filter(category__title__icontains=category)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_product'] = ProductModel.objects.count()
        context['categories'] = ProductCategoryModel.objects.all()
        
        context['filter_by'] = self.request.GET.get('filter-by')

        return context
    

class ShopProductDetailView(DetailView):
    template_name = "shop/product-detail.html"
    queryset = ProductModel.objects.filter(
        status=ProductStatusType.publish.value) 


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        product = self.object
        related_products = ProductModel.objects.filter(
            status=ProductStatusType.publish.value,
            category__in=product.category.all()
        ).exclude(id=product.id).distinct()[:4]

        context["related_products"] = related_products
        return context