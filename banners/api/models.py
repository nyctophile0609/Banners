from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
import datetime
import os
import shutil
from banners.settings import MEDIA_ROOT
from django.http import JsonResponse

LAST_ACTION_CHOICES = [('created', 'Created'),('updated', 'Updated'),('deleted', 'Deleted'),]
BANNER_SIDE_CHOICES=[("front_side","Front"),("back_side","Back"),("both_sides", "Both")]
ADMIN_USER_STATUS_CHOICES =[("high_rank","High"),('middle_rank', 'Middle'),('low_rank', 'Low'),]
BANNER_TYPE_CHOICES = [("on_a_wall","On wall"),('on_a_pole', 'On pole'),('else_where', 'Other'),] 
ORDER_STATUS_CHOICES=[("finished_rent","Finished"),("ongoing_rent","Ongoing"),("planning_rent","Planning")]
MODEL_CHOICES = [('admin_user_model', 'Admin User Model'),('banner_model', 'Banner Model'),
                 ('order_model','Order Model'),("payment_model","Payment Model"),
                 ('outlay_model','Outlay Model'),("bruh_model","Bruh Model")]


class UserModel(AbstractUser):
    username=models.CharField(max_length=100,unique=True)
    full_name=models.CharField(max_length=100)
    admin_status= models.CharField(choices=ADMIN_USER_STATUS_CHOICES,max_length=20)
    ulast_action= models.CharField(choices=LAST_ACTION_CHOICES,max_length=20,)
    created_date=models.DateTimeField(auto_now_add=True)
    def get_extra_actions():
        return [] 

class BannerModel(models.Model):
    added_by=models.ForeignKey(UserModel,on_delete=models.SET_NULL,null=True)
    banner_id=models.CharField(max_length=50)
    name=models.CharField(max_length=150)
    banner_type=models.CharField(choices=BANNER_TYPE_CHOICES,max_length=20)
    latitude=models.DecimalField(max_digits=32, decimal_places=20)
    longitude=models.DecimalField(max_digits=32, decimal_places=20)
    banner_image=models.ImageField(upload_to="just_a_sec")
    blast_action=models.CharField(choices=LAST_ACTION_CHOICES,max_length=20,)
    created_date=models.DateTimeField(auto_now_add=True)
    
   
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        image_instance = self.banner_image
        new_directory_path = os.path.join(MEDIA_ROOT, f"banner_{self.id}")
        if not os.path.exists(new_directory_path):
            os.makedirs(new_directory_path)
        source_image_path = image_instance.path
        _, file_name = os.path.split(source_image_path)
        new_image_path = os.path.join(new_directory_path, file_name)
        try:
            shutil.move(source_image_path, new_image_path)
        except Exception as e:
             return JsonResponse({'success': False, 'error_message':f"Error moving image file: {e}"}, status=400)
        if self.banner_image!=f"banner_{self.id}/{file_name}":
            self.banner_image = f"banner_{self.id}/{file_name}"
            self.save()
    class Meta:
            ordering = ['-created_date']
        

class OrderModel(models.Model):
    order_admin = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True)
    company = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)    
    banner = models.ForeignKey(BannerModel, on_delete=models.SET_NULL, null=True)
    banner_side = models.CharField(choices=BANNER_SIDE_CHOICES, max_length=20)
    rent_price = models.DecimalField(max_digits=32, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    order_status = models.CharField(choices=ORDER_STATUS_CHOICES, max_length=20)
    order_note = models.CharField(max_length=600, null=True, blank=True)
    full_payment = models.DecimalField(max_digits=32, decimal_places=2, null=True)
    paid_payment = models.DecimalField(max_digits=32, decimal_places=2, default=0)
    olast_action = models.CharField(choices=LAST_ACTION_CHOICES, max_length=20)
    created_date = models.DateTimeField(auto_now_add=True)
   
    def clean(self):
        if self.start_date:
            try:
                self.start_date = datetime.datetime.strptime(self.start_date.strftime('%m/%d/%Y'), "%m/%d/%Y")
            except ValueError:
                raise ValidationError({'start_date': 'Invalid date format. Please use mm/dd/yyyy.'})

        if self.end_date:
            try:
                self.end_date = datetime.datetime.strptime(self.end_date.strftime('%m/%d/%Y'), "%m/%d/%Y")
            except ValueError:
                raise ValidationError({'end_date': 'Invalid date format. Please use mm/dd/yyyy.'})

        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                raise ValidationError({'end_date': 'End date must be greater than start date.'})
        
    def save(self, *args, **kwargs): 
        if self.start_date and self.end_date:
            try:
                self.end_date = self.end_date.replace(day=self.start_date.day)
            except ValueError:
                self.end_date = datetime.date(self.end_date.year, self.end_date.month, 28)
                self.start_date = datetime.date(self.start_date.year, self.start_date.month, 28)

        super().save(*args, **kwargs)

    def monthly_payment(self):
        years=self.end_date.year-self.start_date.year
        months=self.end_date.month-self.start_date.month
        return years*12+months
    class Meta:
            ordering = ['-created_date']
class PaymentModel(models.Model):
    admin=models.ForeignKey(UserModel,on_delete=models.SET_NULL,null=True)
    client=models.ForeignKey(OrderModel,on_delete=models.SET_NULL,null=True)
    payment_amount=models.DecimalField(max_digits=32,decimal_places=2)
    plast_action= models.CharField(choices=LAST_ACTION_CHOICES,max_length=20,)
    created_date=models.DateTimeField(auto_now_add=True)
    class Meta:
            ordering = ['-created_date']

class BruhModel(models.Model):
    bruh_admin = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True)
    name=models.CharField(max_length=100)
    number=models.CharField(max_length=30,null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    rent_price = models.DecimalField(max_digits=32, decimal_places=2)
    bruh_note = models.CharField(max_length=600, null=True, blank=True)
    full_payment = models.DecimalField(max_digits=32, decimal_places=2, null=True)
    paid_payment = models.DecimalField(max_digits=32, decimal_places=2, default=0)
    slast_action = models.CharField(choices=LAST_ACTION_CHOICES, max_length=20)
    created_date = models.DateTimeField(auto_now_add=True)
  
    def clean(self):
        if self.start_date:
            try:
                self.start_date = datetime.datetime.strptime(self.start_date.strftime('%m/%d/%Y'), "%m/%d/%Y")
            except ValueError:
                raise ValidationError({'start_date': 'Invalid date format. Please use mm/dd/yyyy.'})
        if self.end_date:
            try:
                self.end_date = datetime.datetime.strptime(self.end_date.strftime('%m/%d/%Y'), "%m/%d/%Y")
            except ValueError:
                raise ValidationError({'end_date': 'Invalid date format. Please use mm/dd/yyyy.'})

        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                raise ValidationError({'end_date': 'End date must be greater than start date.'})
    def save(self, *args, **kwargs):
        if self.start_date and self.end_date:
            try:
                self.end_date = self.end_date.replace(day=self.start_date.day)
            except Exception:
                self.end_date = datetime.date(self.end_date.year, self.end_date.month, 28)
                self.start_date = datetime.date(self.start_date.year, self.start_date.month, 28)
        super().save(*args, **kwargs)

    def monthly_payment(self):
        years=self.end_date.year-self.start_date.year
        months=self.end_date.month-self.start_date.month
        return years*12+months
    class Meta:
            ordering = ['-created_date']


class OutlayModel(models.Model):
    admin=models.ForeignKey(UserModel,on_delete=models.SET_NULL,null=True)
    bruh=models.ForeignKey(BruhModel,on_delete=models.SET_NULL,null=True)
    outlay_amount=models.DecimalField(max_digits=32,decimal_places=2)
    elast_action= models.CharField(choices=LAST_ACTION_CHOICES,max_length=20,)
    created_date=models.DateTimeField(auto_now_add=True)
    class Meta:
            ordering = ['-created_date']

class ActionLogModel(models.Model):


    #For users
    user_id=models.PositiveBigIntegerField()
    #For objects
    object_model=models.CharField(choices=MODEL_CHOICES, max_length=30)
    object_id = models.PositiveIntegerField()
    shadow_object_id=models.PositiveIntegerField(null=True)
    #For action
    action_type = models.CharField(choices=LAST_ACTION_CHOICES, max_length=10)

    timestamp = models.DateTimeField(auto_now_add=True)
    class Meta:
            ordering = ['-timestamp']
#Shadow Models
class ShadowUserModel(models.Model):
    user_object_id=models.PositiveIntegerField()
    username=models.CharField(max_length=100)
    full_name=models.CharField(max_length=100)
    admin_status= models.CharField(choices=ADMIN_USER_STATUS_CHOICES,max_length=20)
    ulast_action= models.CharField(choices=LAST_ACTION_CHOICES,max_length=20,)

class ShadowBannerModel(models.Model):
    banner_object_id=models.PositiveIntegerField()
    added_by=models.ForeignKey(UserModel,on_delete=models.SET_NULL,null=True)
    banner_id=models.CharField(max_length=50)
    name=models.CharField(max_length=150)
    banner_type=models.CharField(choices=BANNER_TYPE_CHOICES,max_length=20)
    latitude=models.DecimalField(max_digits=20, decimal_places=10)
    longitude=models.DecimalField(max_digits=20, decimal_places=10)
    banner_image=models.ImageField(upload_to="just_a_sec")
    blast_action=models.CharField(choices=LAST_ACTION_CHOICES,max_length=20,)

class ShadowOrderModel(models.Model):
    order_object_id=models.PositiveIntegerField()
    order_admin = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True)
    company = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)    
    banner = models.ForeignKey(BannerModel, on_delete=models.SET_NULL, null=True)
    banner_side = models.CharField(choices=BANNER_SIDE_CHOICES, max_length=20)
    rent_price = models.DecimalField(max_digits=32, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    order_status = models.CharField(choices=ORDER_STATUS_CHOICES, max_length=20)
    order_note = models.CharField(max_length=600, null=True, blank=True)
    full_payment = models.DecimalField(max_digits=32, decimal_places=2, null=True)
    paid_payment = models.DecimalField(max_digits=32, decimal_places=2, default=0)
    olast_action = models.CharField(choices=LAST_ACTION_CHOICES, max_length=20)

class ShadowPaymentModel(models.Model):
    payment_object_id=models.PositiveIntegerField()
    admin=models.ForeignKey(UserModel,on_delete=models.SET_NULL,null=True)
    client=models.ForeignKey(OrderModel,on_delete=models.SET_NULL,null=True)
    payment_amount=models.DecimalField(max_digits=32,decimal_places=2)
    plast_action= models.CharField(choices=LAST_ACTION_CHOICES,max_length=20,)

class ShadowOutlayModel(models.Model):
    outlay_object_id=models.PositiveIntegerField()
    bruh=models.ForeignKey(BruhModel,on_delete=models.SET_NULL,null=True) 
    admin=models.ForeignKey(UserModel,on_delete=models.SET_NULL,null=True)
    outlay_amount=models.DecimalField(max_digits=32,decimal_places=2)
    elast_action= models.CharField(choices=LAST_ACTION_CHOICES,max_length=20,)

class ShadowBruhModel(models.Model):
    bruh_object_id=models.PositiveIntegerField()
    name=models.CharField(max_length=100)
    number=models.CharField(max_length=30,null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    rent_price = models.DecimalField(max_digits=32, decimal_places=2)
    bruh_note = models.CharField(max_length=600, null=True, blank=True)
    full_payment = models.DecimalField(max_digits=32, decimal_places=2, null=True)
    paid_payment = models.DecimalField(max_digits=32, decimal_places=2, default=0)
    slast_action = models.CharField(choices=LAST_ACTION_CHOICES, max_length=20)
