# Generated by Django 5.1.5 on 2025-04-01 02:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TaxCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_uid', models.IntegerField(blank=True, null=True)),
                ('write_uid', models.IntegerField(blank=True, null=True)),
                ('branch_id', models.IntegerField(blank=True, null=True)),
                ('company_id', models.IntegerField(blank=True, null=True)),
                ('create_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('write_date', models.DateTimeField(auto_now=True, null=True)),
                ('code', models.CharField(blank=True, editable=False, unique=True)),
                ('name', models.CharField(blank=True, max_length=255)),
                ('description', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'db_table': 'tax_category',
            },
        ),
        migrations.CreateModel(
            name='Tax',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_uid', models.IntegerField(blank=True, null=True)),
                ('write_uid', models.IntegerField(blank=True, null=True)),
                ('branch_id', models.IntegerField(blank=True, null=True)),
                ('company_id', models.IntegerField(blank=True, null=True)),
                ('create_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('write_date', models.DateTimeField(auto_now=True, null=True)),
                ('code', models.CharField(blank=True, editable=False, unique=True)),
                ('name', models.CharField(blank=True, max_length=255)),
                ('amount', models.DecimalField(decimal_places=6, default=0, max_digits=19)),
                ('amount_type', models.CharField(choices=[('percentage', 'Percentage'), ('fixed_value', 'Fixed value')], max_length=50)),
                ('type', models.CharField(choices=[('sale', 'Sale Tax'), ('purchase', 'Purchase Tax'), ('withholding', 'Withholding Tax')], max_length=50)),
                ('tax_option', models.CharField(choices=[('tax_inclusive', 'Tax Inclusive'), ('tax_exclusive', 'Tax Exclusive')], default='tax_exclusive', max_length=50)),
                ('tax_discount_option', models.CharField(choices=[('after_discount', 'After Discount'), ('before_discount', 'Before Discount')], default='after_discount', max_length=50)),
                ('is_active', models.BooleanField(default=False)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('tax_categories', models.ManyToManyField(db_table='tax_category_tax_rel', related_name='taxes', to='tax.taxcategory')),
            ],
            options={
                'db_table': 'tax',
            },
        ),
    ]
