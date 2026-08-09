import openpyxl
from django.contrib import admin
from django.http import HttpResponse

from .models import (
    BlogCategoryModel,
    BlogModel,
    NewsLetterModel,
)


# اکشن خروجی گرفتن اکسل برای خبرنامه
@admin.action(description="خروجی اکسل از شماره‌های انتخاب شده")
def export_to_excel(modeladmin, request, queryset):
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="newsletter_phone_numbers.xlsx"'

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "شماره‌های خبرنامه"

    headers = ["شناسه", "شماره تلفن"]
    ws.append(headers)

    for obj in queryset:
        ws.append([obj.id, obj.phone_number])

    wb.save(response)
    return response


# ۱. ادمین خبرنامه
@admin.register(NewsLetterModel)
class NewsLetterModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone_number')
    search_fields = ('phone_number',)
    actions = [export_to_excel]


# ۲. ادمین بلاگ
@admin.register(BlogModel)
class BlogModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'title', 'reading_time', 'status', 'views']


# ۳. ادمین دسته‌بندی بلاگ
@admin.register(BlogCategoryModel)
class BlogCategoryModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']