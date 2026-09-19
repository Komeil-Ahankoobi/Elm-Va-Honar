from django.core.management.base import BaseCommand
from order.models import OrderModel


class Command(BaseCommand):
    help = "سفارش‌های در انتظار پرداختِ منقضی‌شده رو cancel/delete می‌کنه"

    def handle(self, *args, **options):
        OrderModel.expire_stale_pending()
        self.stdout.write(self.style.SUCCESS("پاک‌سازی سفارش‌های منقضی انجام شد"))