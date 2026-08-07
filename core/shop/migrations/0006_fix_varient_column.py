from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_productvarientmodel'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'shop_productvarientmodel'
                    AND column_name = 'varient_type'
                ) THEN
                    ALTER TABLE shop_productvarientmodel
                        RENAME COLUMN varient_type TO variant_type;
                END IF;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]