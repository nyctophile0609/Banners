# Generated by Django 5.0.4 on 2024-05-07 10:17

import django.contrib.auth.models
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionLogModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.PositiveBigIntegerField()),
                ('object_model', models.CharField(choices=[('admin_user_model', 'Admin User Model'), ('banner_model', 'Banner Model'), ('order_model', 'Order Model'), ('payment_model', 'Payment Model'), ('outlay_model', 'Outlay Model')], max_length=30)),
                ('object_id', models.PositiveIntegerField()),
                ('shadow_object_id', models.PositiveIntegerField(null=True)),
                ('action_type', models.CharField(choices=[('created', 'Created'), ('updated', 'Updated'), ('deleted', 'Deleted')], max_length=10)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='ShadowUserModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_object_id', models.PositiveIntegerField()),
                ('username', models.CharField(max_length=100)),
                ('full_name', models.CharField(max_length=100)),
                ('admin_status', models.CharField(choices=[('high_rank', 'High'), ('middle_rank', 'Middle'), ('low_rank', 'Low')], max_length=20)),
                ('ulast_action', models.CharField(choices=[('created', 'Created'), ('updated', 'Updated'), ('deleted', 'Deleted')], max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='UserModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(max_length=100, unique=True)),
                ('full_name', models.CharField(max_length=100)),
                ('admin_status', models.CharField(choices=[('high_rank', 'High'), ('middle_rank', 'Middle'), ('low_rank', 'Low')], max_length=20)),
                ('ulast_action', models.CharField(choices=[('created', 'Created'), ('updated', 'Updated'), ('deleted', 'Deleted')], max_length=20)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='BannerModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('banner_id', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=150)),
                ('banner_type', models.CharField(choices=[('on_a_wall', 'On wall'), ('on_a_pole', 'On pole'), ('else_where', 'Other')], max_length=20)),
                ('latitude', models.DecimalField(decimal_places=20, max_digits=32)),
                ('longitude', models.DecimalField(decimal_places=20, max_digits=32)),
                ('banner_image', models.ImageField(upload_to='just_a_sec')),
                ('blast_action', models.CharField(choices=[('created', 'Created'), ('updated', 'Updated'), ('deleted', 'Deleted')], max_length=20)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('added_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_date'],
            },
        ),
        migrations.CreateModel(
            name='OrderModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.CharField(max_length=100)),
                ('phone_number', models.CharField(max_length=100)),
                ('banner_side', models.CharField(choices=[('front_side', 'Front'), ('back_side', 'Back'), ('both_sides', 'Both')], max_length=20)),
                ('rent_price', models.DecimalField(decimal_places=2, max_digits=32)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('order_status', models.CharField(choices=[('finished_rent', 'Finished'), ('ongoing_rent', 'Ongoing'), ('planning_rent', 'Planning')], max_length=20)),
                ('order_note', models.CharField(blank=True, max_length=600, null=True)),
                ('full_payment', models.DecimalField(decimal_places=2, max_digits=32, null=True)),
                ('paid_payment', models.DecimalField(decimal_places=2, default=0, max_digits=32)),
                ('olast_action', models.CharField(choices=[('created', 'Created'), ('updated', 'Updated'), ('deleted', 'Deleted')], max_length=20)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('banner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.bannermodel')),
                ('order_admin', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_date'],
            },
        ),
        migrations.CreateModel(
            name='OutlayModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('outlay_amount', models.DecimalField(decimal_places=2, max_digits=32)),
                ('elast_action', models.CharField(choices=[('created', 'Created'), ('updated', 'Updated'), ('deleted', 'Deleted')], max_length=20)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('admin', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_date'],
            },
        ),
        migrations.CreateModel(
            name='PaymentModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_amount', models.DecimalField(decimal_places=2, max_digits=32)),
                ('plast_action', models.CharField(choices=[('created', 'Created'), ('updated', 'Updated'), ('deleted', 'Deleted')], max_length=20)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('admin', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.ordermodel')),
            ],
            options={
                'ordering': ['-created_date'],
            },
        ),
        migrations.CreateModel(
            name='ShadowBannerModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('banner_object_id', models.PositiveIntegerField()),
                ('banner_id', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=150)),
                ('banner_type', models.CharField(choices=[('on_a_wall', 'On wall'), ('on_a_pole', 'On pole'), ('else_where', 'Other')], max_length=20)),
                ('latitude', models.DecimalField(decimal_places=10, max_digits=20)),
                ('longitude', models.DecimalField(decimal_places=10, max_digits=20)),
                ('banner_image', models.ImageField(upload_to='just_a_sec')),
                ('blast_action', models.CharField(choices=[('created', 'Created'), ('updated', 'Updated'), ('deleted', 'Deleted')], max_length=20)),
                ('added_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ShadowOrderModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_object_id', models.PositiveIntegerField()),
                ('company', models.CharField(max_length=100)),
                ('phone_number', models.CharField(max_length=100)),
                ('banner_side', models.CharField(choices=[('front_side', 'Front'), ('back_side', 'Back'), ('both_sides', 'Both')], max_length=20)),
                ('rent_price', models.DecimalField(decimal_places=2, max_digits=32)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('order_status', models.CharField(choices=[('finished_rent', 'Finished'), ('ongoing_rent', 'Ongoing'), ('planning_rent', 'Planning')], max_length=20)),
                ('order_note', models.CharField(blank=True, max_length=600, null=True)),
                ('full_payment', models.DecimalField(decimal_places=2, max_digits=32, null=True)),
                ('paid_payment', models.DecimalField(decimal_places=2, default=0, max_digits=32)),
                ('olast_action', models.CharField(choices=[('created', 'Created'), ('updated', 'Updated'), ('deleted', 'Deleted')], max_length=20)),
                ('banner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.bannermodel')),
                ('order_admin', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ShadowOutlayModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('outlay_object_id', models.PositiveIntegerField()),
                ('outlay_amount', models.DecimalField(decimal_places=2, max_digits=32)),
                ('elast_action', models.CharField(choices=[('created', 'Created'), ('updated', 'Updated'), ('deleted', 'Deleted')], max_length=20)),
                ('admin', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ShadowPaymentModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_object_id', models.PositiveIntegerField()),
                ('payment_amount', models.DecimalField(decimal_places=2, max_digits=32)),
                ('plast_action', models.CharField(choices=[('created', 'Created'), ('updated', 'Updated'), ('deleted', 'Deleted')], max_length=20)),
                ('admin', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.ordermodel')),
            ],
        ),
    ]