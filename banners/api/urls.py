from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from django.conf.urls.static import static


router = DefaultRouter()

router.register(r'users',UserModelViewSet,basename='users')
router.register(r'banners',BannerModelViewSet,basename='banners')
router.register(r'companies',CompanyModelViewSet,basename='companies')
router.register(r'orders',OrderModelViewSet,basename='orders')
router.register(r'payments',PaymentModelViewSet,basename='payments')
router.register(r"outlays",OutlayModelViewSet,basename="outlays")
router.register(r'bruhs',BruhModelViewSet,basename='bruhs')
router.register(r'action-log',ActionLogModelViewSet,basename='action-log')


urlpatterns = [
    path('orders/monthly_income/<int:year>/', OrderModelViewSet.as_view({'get': 'monthly_income'}), name='order_monthly_income'),
    path('bruhs/monthly_income/<int:year>/', BruhModelViewSet.as_view({'get': 'monthly_income'}), name='bruh_monthly_income'),
    path('orders/detailed_orders/<int:id>/', OrderModelViewSet.as_view({'get': 'detailed_orders'}), name='detailed_orders'),
    
    path('', include(router.urls)),
]