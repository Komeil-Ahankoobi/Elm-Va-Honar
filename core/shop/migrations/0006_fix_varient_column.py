from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_productvarientmodel'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE shop_productvarientmodel RENAME COLUMN varient_type TO variant_type;",
            reverse_sql="ALTER TABLE shop_productvarientmodel RENAME COLUMN variant_type TO varient_type;",
        ),
    ]