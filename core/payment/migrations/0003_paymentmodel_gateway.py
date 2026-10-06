from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0002_paymentmodel_card_hash_paymentmodel_card_pan_and_more"),
    ]

    operations = [
        # ردیف‌های قدیمی همگی زرین‌پال هستند، پس default کافی است.
        migrations.AddField(
            model_name="paymentmodel",
            name="gateway",
            field=models.CharField(
                choices=[
                    ("zarinpal", "پرداخت با زرین‌پال"),
                    ("parsian", "پرداخت با بانک پارسیان"),
                ],
                db_index=True,
                default="zarinpal",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="paymentmodel",
            name="authority_id",
            field=models.CharField(db_index=True, max_length=64),
        ),
        migrations.AddConstraint(
            model_name="paymentmodel",
            constraint=models.UniqueConstraint(
                fields=("gateway", "authority_id"), name="unique_gateway_authority"
            ),
        ),
    ]
