from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import *
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
class UserModelSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserModel
        fields = ["id", "username", "full_name", "admin_status", "password", "created_date", "ulast_action"]
        read_only_fields = ["id",  "created_date","ulast_action"]
        action_fields = {
            'list': {'fields': ('password')}
        }    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = UserModel.objects.create(**validated_data)
        user.set_password(password)
        user.ulast_action="created"
        user.save()
        ad1(uid=self.context['request'].user.id,oid=user.id,mnum=1,at='created',shid=None)
        return user
    
    def update(self, instance, validated_data):
        shadow=ShadowUserModel.objects.create(
            user_object_id=instance.id,
            username=instance.username,
            full_name=instance.full_name,
            admin_status=instance.admin_status,
            ulast_action=instance.ulast_action,
        )
        instance.ulast_action = "updated"
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        instance.__dict__.update(**validated_data)
        instance.save()
        ad1(uid=self.context['request'].user.id,oid=instance.id,mnum=1,at='updated',shid=shadow.id)
        return instance

class BannerModelSerializer(ModelSerializer):
    class Meta:
        model = BannerModel
        fields =["id","added_by","banner_id","name","banner_type","latitude","longitude","banner_image","blast_action","created_date"]
        read_only_fields = ['id', 'created_date', 'blast_action',"added_by"] 
    def create(self, validated_data):
        banner = BannerModel.objects.create(**validated_data)
        banner.blast_action = "created"
        banner.added_by=self.context["request"].user
        banner.save()
        ad1(uid=self.context['request'].user.id, oid=banner.id, mnum=2, at='created',shid=None)
        return banner

    def update(self, instance, validated_data):
        shadow=ShadowBannerModel.objects.create(
            banner_object_id=instance.id,
            added_by=instance.added_by,
            banner_id=instance.banner_id,
            name=instance.name,
            latitude=instance.latitude,
            longitude=instance.longitude,
            banner_image=instance.banner_image,
            blast_action=instance.blast_action,
        )
        instance.banner_id=validated_data.get("banner_id",instance.banner_id)
        instance.name=validated_data.get("name",instance.name)
        instance.latitude=validated_data.get("latitude",instance.latitude)
        instance.longitude=validated_data.get("longitude",instance.longitude)
        instance.blast_action = "updated"
        instance.banner_image=validated_data.get("banner_image",instance.banner_image)
        ad1(uid=self.context['request'].user.id, oid=instance.id, mnum=2, at='updated',shid=shadow.id)
        instance.save()

        
        return instance

class OrderModelSerializer(ModelSerializer):
    monthly_payment = serializers.CharField( read_only=True)
    orders = serializers.CharField( read_only=True)

    class Meta:
        model=OrderModel
        fields="__all__"
        read_only_fields = ["id", "created_date","olast_action","order_admin","monthly_payment","full_payment","paid_payment","orders"]

    def create(self, validated_data):
        order=OrderModel.objects.create(**validated_data)
        order.olast_action="created"
        order.order_admin=self.context["request"].user
        years=order.end_date.year-order.start_date.year
        months=order.end_date.month-order.start_date.month
        order.full_payment=int(years*12+months)*order.rent_price
        order.save()
        ad1(uid=self.context['request'].user.id,oid=order.id,mnum=3,at='created',shid=None)
        return order

    def update(self, instance, validated_data):
        shadow=ShadowOrderModel.objects.create(
            order_object_id=instance.id,
            order_admin=instance.order_admin,
            company=instance.company,
            phone_number=instance.phone_number,
            banner=instance.banner,
            banner_side=instance.banner_side,
            rent_price=instance.rent_price,
            start_date=instance.start_date,
            end_date=instance.end_date,
            order_status=instance.order_status,
            order_note=instance.order_note,
            paid_payment=instance.paid_payment,
            olast_action=instance.olast_action,)
        
        instance.phone_number=validated_data.get("phone_number",instance.phone_number)
        instance.company = validated_data.get('company', instance.company)
        instance.banner_side = validated_data.get('banner_side', instance.banner_side)
        instance.rent_price = validated_data.get('rent_price', instance.rent_price)
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.end_date = validated_data.get('end_date', instance.end_date)
        instance.order_admin=self.context["request"].user
        years=instance.end_date.year-instance.start_date.year
        months=instance.end_date.month-instance.start_date.month
        instance.order_note=validated_data.get("order_note",instance.order_note)
        instance.full_payment=int(years*12+months)*instance.rent_price
        instance.olast_action = "updated"
        instance.save()
        ad1(uid=self.context['request'].user.id, oid=instance.id, mnum=3, at='updated',shid=shadow.id)
        return instance

class PaymentModelSerializer(ModelSerializer):
    client1=OrderModelSerializer(read_only=True)
    admin=UserModelSerializer(read_only=True)
    class Meta:
        model=PaymentModel
        fields="__all__"
        read_only_fields=["admin","plast_action","created_date","admin","client1"]
  

    def create(self, validated_data):
        payment = PaymentModel.objects.create(**validated_data)
        payment.plast_action = "created"
        payment.admin=self.context["request"].user
        order_object=payment.client
        if payment.payment_amount>order_object.full_payment-order_object.paid_payment:
            return JsonResponse({'success': False, 'error_message': 'Payment amount cannot exceed the remaining balance of the order.'}, status=400)
        else:
            order_object.paid_payment=payment.payment_amount+order_object.paid_payment
            order_object.save()
            payment.save()
            ad1(uid=self.context['request'].user.id, oid=payment.id, mnum=4, at='created',shid=None)
            return payment

    def update(self, instance, validated_data):
        new_payment=validated_data.get("payment_amount")
        new_order=get_object_or_404(OrderModel,id=validated_data.get("order_object").id)
        if new_payment>new_order.full_payment-new_order.paid_payment:
            return JsonResponse({'success': False, 'error_message': 'Payment amount cannot exceed the remaining balance of the order.'}, status=400)
        if instance.client.paid_payment<instance.payment_amount:
            return JsonResponse({'success': False, 'error_message': 'Payment amount cannot be less than the paid balance of the order.'}, status=400)
        else:
            shadow=ShadowPaymentModel.objects.create(
                payment_object_id=instance.id,
                admin=instance.admin,
                client=instance.client,
                payment_amount=instance.payment_amount,
                plast_action=instance.plast_action,
            )

            client1=get_object_or_404(OrderModel,id=instance.client.id)
            client1.paid_payment=client1.paid_payment-instance.payment_amount
            client1.save()

            instance.plast_action = "updated"
            instance.payment_amount=new_payment
            instance.client=new_order
            instance.save()
            order_object =get_object_or_404(OrderModel,id=instance.client.id)
            order_object.paid_payment=order_object.paid_payment+instance.payment_amount
            order_object.save()
            ad1(uid=self.context['request'].user.id, oid=instance.id, mnum=4, at='updated',shid=shadow.id)
            return instance

class OutlayModelSerializer(ModelSerializer):
    admin=UserModelSerializer(read_only=True)
    class Meta:
        model=OutlayModel
        fields="__all__"
        read_only_fields=["id","admin","elast_action"]

    def create(self, validated_data):
        outlay=OutlayModel.objects.create(**validated_data)
        outlay.elast_action="created"
        outlay.admin=self.context["request"].user
        outlay.save()
        ad1(uid=self.context['request'].user.id, oid=outlay.id, mnum=5, at='created',shid=None)
        return outlay

    def update(self, instance, validated_data):
        shadow=ShadowOutlayModel.objects.create(
            outlay_object_id=instance.id,
            admin=instance.admin,
            outlay_amount=instance.outlay_amount,
            elast_action=instance.elast_action,
        )
        instance.elast_action = "updated"
        instance.outlay_amount=validated_data.get('outlay_amount', instance.outlay_amount)
        instance.save()
        ad1(uid=self.context['request'].user.id, oid=instance.id, mnum=5, at='updated',shid=shadow.id)

        return instance

from rest_framework import serializers
from .models import ActionLogModel
from .models import *

class ActionLogModelSerializer(serializers.ModelSerializer):
    object_instance = serializers.SerializerMethodField()

    class Meta:
        model = ActionLogModel
        fields = '__all__'

    def get_object_instance(self, obj):
        object_model = obj.object_model
        object_id = obj.object_id
        user_id = obj.user_id

        try:
            user = UserModel.objects.values("username").get(id=user_id)
            object_instance = None
            
            if object_model == 'user_model':
                user_instance = UserModel.objects.get(id=object_id)
                object_instance = {'username': user_instance.username}
            elif object_model == 'banner_model':
                object_instance = BannerModel.objects.values("name").get(id=object_id)
            elif object_model == 'order_model':
                object_instance = OrderModel.objects.values("company").get(id=object_id)
            elif object_model == 'payment_model':
                object_instance = PaymentModel.objects.values("admin__username", "client__company", "payment_amount").get(id=object_id)
            elif object_model == 'outlay_model':
                object_instance = OutlayModel.objects.values("admin__username", "outlay_amount").get(id=object_id)
            

            return {
                'user': user['username'],
                'object_instance': object_instance
            }
        except:
            return None

def ad1(oid,uid,mnum,at,shid):
    x=['user_model','banner_model','order_model','payment_model','outlay_model'][int(mnum)-1]
    new_action = ActionLogModel.objects.create(
        user_id=uid,
        object_model=x,
        object_id=oid,
        shadow_object_id=shid,
        action_type=at)
    if new_action:
        return True
    return False