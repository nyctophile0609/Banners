from rest_framework.response import Response
from rest_framework import status, permissions, authentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import *
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .serializers import *
from .models import *
from .permissions import *
from django.http import JsonResponse


class UserModelViewSet(ModelViewSet):
    queryset = UserModel.objects.all().exclude(ulast_action="deleted")
    serializer_class = UserModelSerializer
    authentication_classes = [
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    ]

    @action(detail=False, methods=["post"])
    def login(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

    @action(detail=False, methods=["post"])
    def logout(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.ulast_action = "deleted"
        instance.save()
        ad1(uid=self.request.user.id, oid=instance.id, mnum=1, at="deleted")

    def get_permissions(self):
        if self.action == "logout":
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == "update":
            permission_classes = [permissions.IsAuthenticated, CanUpdateProfile]
        elif self.action == "create" or self.action == "destroy":
            permission_classes = [permissions.IsAuthenticated, IsAdminPermission]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]


class BannerModelViewSet(ModelViewSet):
    queryset = BannerModel.objects.all().exclude(blast_action="deleted")
    serializer_class = BannerModelSerializer
    permission_classes = [permissions.IsAuthenticated]

    authentication_classes = [
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    ]

    def perform_destroy(self, instance):
        instance.blast_action = "deleted"
        instance.save()
        ad1(uid=self.request.user.id, oid=instance.id, mnum=2, at="deleted")


class OrderModelViewSet(ModelViewSet):
    queryset = OrderModel.objects.all().exclude(olast_action="deleted")
    serializer_class = OrderModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    ]

    def perform_destroy(self, instance):
        instance.olast_action = "deleted"
        instance.save()
        ad1(uid=self.request.user.id, oid=instance.id, mnum=3, at="deleted")

    @action(detail=False, methods=["get"])
    def monthly_income(self, request, year=None):
        target_year = year if year != None else datetime.datetime.now().year
        result1 = [0] * 12
        result2 = [0] * 12
        bruhs = OrderModel.objects.filter(
            start_date__year__lte=target_year, end_date__year__gte=target_year
        ).exclude(olast_action="deleted")
        for i in bruhs:
            target_year_start = datetime.date(target_year, 1, 1)
            target_year_end = datetime.date(target_year, 12, 31)  # Adjusted end date
            start_date = max(i.start_date, target_year_start)
            end_date = min(i.end_date, target_year_end)
            rented_months_target_year = (
                (end_date.year - start_date.year) * 12
                + end_date.month
                - start_date.month
                + 1
            )  # Adjusted calculation
            paid_months = i.paid_payment // i.rent_price
            asd = i.paid_payment % i.rent_price
            months_before_target_year = (
                (start_date.year - i.start_date.year) * 12
                + start_date.month
                - i.start_date.month
            )
            paid_months_target_year = int(
                min(
                    max(0, paid_months - months_before_target_year),
                    rented_months_target_year,
                )
            )
            if i.end_date.year > target_year:
                x1 = start_date.month
                x2 = end_date.month + 1
                y1 = start_date.month
                y2 = start_date.month + paid_months_target_year
            if i.end_date.year == target_year:
                x1 = start_date.month
                x2 = end_date.month
                y1 = start_date.month
                y2 = start_date.month + paid_months_target_year
            for j in range(x1, x2):
                result1[j - 1] += i.rent_price

            for d in range(y1, y2):
                if d <= 12:
                    result2[d - 1] += i.rent_price
                if d == y2 - 1:
                    result2[d] += asd
        qw2 = dict()
        for e in range(1, 13):
            qw2[e] = result1[e - 1] - result2[e - 1]
        print(result1, result2)

        qwer = dict()
        qwer["year"] = target_year
        qwer["you_need_this"] = qw2
        qwer["paid_payment"] = result2
        qwer["yearly_payment"] = sum(result2)
        return Response(qwer)

    @action(detail=False, methods=["get"])
    def yearly_income(self, request, year=None):
        target_year = year if year != None else datetime.datetime.now().year
        result = 0
        result1 = 0
        result2 = 0
        orders = OrderModel.objects.filter(
            start_date__year__lte=target_year, end_date__year__gte=target_year
        ).exclude(olast_action="deleted")
        orders1 = OrderModel.objects.filter(
            start_date__year__lte=target_year,
            end_date__year__gte=target_year,
            olast_action="deleted",
        )
        for i in orders:
            if i.start_date.year == target_year:
                rented_months_target_year = min(
                    13 - i.start_date.month, i.monthly_payment()
                )
                paid_months = i.paid_payment // i.rent_price
                paid_months_target_year = (
                    min(paid_months, rented_months_target_year)
                    if paid_months >= 0
                    else 0
                )
            else:
                paid_months = i.paid_payment // i.rent_price
                months_before_target_year = (
                    (target_year - i.start_date.year) * 12 + 1 - i.start_date.month
                )
                j = i.monthly_payment() - months_before_target_year
                rented_months_target_year = min(j, 12) if j >= 0 else 0
                h = paid_months - months_before_target_year
                paid_months_target_year = (
                    min(h, rented_months_target_year) if h >= 0 else 0
                )
            result += paid_months_target_year * i.rent_price
        for i in orders1:
            if i.start_date.year == target_year:
                rented_months_target_year = min(
                    13 - i.start_date.month, i.monthly_payment()
                )
                paid_months = i.paid_payment // i.rent_price
                paid_months_target_year = (
                    min(paid_months, rented_months_target_year)
                    if paid_months >= 0
                    else 0
                )
            else:
                paid_months = i.paid_payment // i.rent_price
                months_before_target_year = (
                    (target_year - i.start_date.year) * 12 + 1 - i.start_date.month
                )
                j = i.monthly_payment() - months_before_target_year
                rented_months_target_year = min(j, 12) if j >= 0 else 0
                h = paid_months - months_before_target_year
                paid_months_target_year = (
                    min(h, rented_months_target_year) if h >= 0 else 0
                )
            result2 += paid_months_target_year * i.rent_price
        w = {"year": target_year, "yearly_payment": result}
        return Response(w)

    def get_serializer_class(self):
        if self.action in ["monthly_income", "yearly_income"]:
            return None
        return super().get_serializer_class()


class PaymentModelViewSet(ModelViewSet):
    queryset = PaymentModel.objects.all().exclude(plast_action="deleted")
    serializer_class = PaymentModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    ]

    def perform_destroy(self, instance):
        instance.plast_action = "deleted"
        instance.save()
        order_object = get_object_or_404(OrderModel, id=instance.client.id)
        order_object.paid_payment = order_object.paid_payment - instance.payment_amount
        order_object.save()
        ad1(uid=self.request.user.id, oid=instance.id, mnum=4, at="deleted")


class OutlayModelViewSet(ModelViewSet):
    queryset = OutlayModel.objects.all().exclude(elast_action="deleted")
    serializer_class = OutlayModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    ]

    def perform_destroy(self, instance):
        instance.elast_action = "deleted"
        instance.save()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return OutlayModelSerializer1
        return OutlayModelSerializer

    @action(detail=False, methods=["get"])
    def monthly_expenses(self, request, year=None):
        result = [0] * 12
        target_year = year if year != None else datetime.datetime.now().year
        outlays = OutlayModel.objects.filter(created_date__year=target_year).exclude(
            elast_action="deleted"
        )
        for i in outlays:
            result[i.created_date.month - 1] += i.outlay_amount
        dick = dict()
        for i in range(1, 13):
            dick[i] = result[i - 1]
        qw = dict()
        qw["year"] = target_year
        qw["monthly_expenses"] = dick
        qw["yearly_expenses"] = sum(result)
        return Response(qw)

    @action(detail=False, methods=["get"])
    def home_page_details(self, request):
        q1 = OrderModel.objects.all().exclude(olast_action="deleted")
        w1 = q1.count()
        q2 = UserModel.objects.all().exclude(ulast_action="deleted")
        w2 = q2.count()
        q3 = BannerModel.objects.all().exclude(blast_action="deleted")
        w3 = q3.count()
        return Response({"admins": w2, "banners": w3, "orders": w1})


class BruhModelViewSet(ModelViewSet):
    queryset = BruhModel.objects.all().exclude(slast_action="deleted")
    serializer_class = BruhModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    ]

    def perform_destroy(self, instance):
        instance.slast_action = "deleted"
        instance.save()
        ad1(uid=self.request.user.id, oid=instance.id, mnum=6, at="deleted")

    @action(detail=False, methods=["get"])
    def monthly_income(self, request, year=None):
        target_year = year if year is not None else datetime.datetime.now().year
        result1 = [0] * 12
        result2 = [0] * 12
        rer = [
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
        ]
        bruhs = BruhModel.objects.filter(
            start_date__year__lte=target_year, end_date__year__gte=target_year
        ).exclude(slast_action="deleted")
        for bruh in bruhs:
            target_year_start = datetime.date(target_year, 1, 1)
            target_year_end = datetime.date(target_year, 12, 31)
            start_date = max(bruh.start_date, target_year_start)
            end_date = min(bruh.end_date, target_year_end)
            rented_months_target_year = (
                (end_date.year - start_date.year) * 12
                + end_date.month
                - start_date.month
                + 1
            )
            paid_months = bruh.paid_payment // bruh.rent_price
            asd = bruh.paid_payment % bruh.rent_price
            months_before_target_year = (
                (start_date.year - bruh.start_date.year) * 12
                + start_date.month
                - bruh.start_date.month
            )
            paid_months_target_year = int(
                min(
                    max(0, paid_months - months_before_target_year),
                    rented_months_target_year,
                )
            )

            if bruh.end_date.year > target_year:
                x1 = start_date.month
                x2 = end_date.month + 1
                y1 = start_date.month
                y2 = start_date.month + paid_months_target_year
            if bruh.end_date.year == target_year:
                x1 = start_date.month
                x2 = end_date.month
                y1 = start_date.month
                y2 = start_date.month + paid_months_target_year

            for j in range(x1, x2):

                result1[j - 1] += bruh.rent_price

            for vv in range(x1, x2):
                if y2 == vv:
                    cw = {"label": bruh.name, "data": bruh.rent_price - asd}
                elif y2 > vv:
                    cw = {"label": bruh.name, "data": 0}
                else:
                    cw = {"label": bruh.name, "data": bruh.rent_price}
                rer[vv - 1].append(cw)

            for d in range(y1, y2):
                if d <= 12:
                    result2[d - 1] += bruh.rent_price
                if d == y2 - 1:
                    result2[d] += asd

        qw2 = dict()
        for e in range(1, 13):
            qw2[e] = result1[e - 1] - result2[e - 1]
        qwer = dict()
        qwer["year"] = target_year
        qwer["you_need_this"] = qw2
        qwer["paid_payment"] = result2
        qwer["yearly_payment"] = sum(result2)
        qwer["hh"] = rer
        return Response(qwer)


class ActionLogModelViewSet(ModelViewSet):
    queryset = ActionLogModel.objects.all()
    serializer_class = ActionLogModelSerializer
    authentication_classes = [
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    ]

    def perform_destroy(self, instance):
        if instance.object_model == "user_model":
            if instance.action_type == "created":
                user = get_object_or_404(UserModel, id=instance.object_id)
                user.delete()
            elif instance.action_type == "deleted":
                user = get_object_or_404(UserModel, id=instance.object_id)
                user.ulast_action = "created"
            elif instance.action_type == "updated":
                user = get_object_or_404(UserModel, id=instance.object_id)
                shadow = get_object_or_404(
                    ShadowUserModel, id=instance.shadow_object_id
                )
                user.username = shadow.username
                user.full_name = shadow.full_name
                user.admin_status = shadow.admin_status
                user.ulast_action = shadow.ulast_action
                user.save()
                shadow.delete()

        elif instance.object_model == "banner_model":
            if instance.action_type == "created":
                banner = get_object_or_404(BannerModel, id=instance.object_id)
                banner.delete()

            elif instance.action_type == "deleted":
                banner = get_object_or_404(BannerModel, id=instance.object_id)
                banner.blast_action = "created"
                banner.save()
            elif instance.action_type == "updated":
                banner = get_object_or_404(BannerModel, id=instance.object_id)
                shadow = get_object_or_404(
                    ShadowBannerModel, id=instance.shadow_object_id
                )
                banner.banner_id = shadow.banner_id
                banner.name = shadow.name
                banner.banner_type = shadow.banner_type
                banner.latitude = shadow.latitude
                banner.longitude = shadow.longitude
                banner.banner_image = shadow.banner_image
                banner.blast_action = shadow.blast_action
                banner.save()
                shadow.delete()
        elif instance.object_model == "order_model":
            if instance.action_type == "created":
                order = get_object_or_404(OrderModel, id=instance.object_id)
                order.delete()
            elif instance.action_type == "deleted":
                order = get_object_or_404(OrderModel, id=instance.object_id)
                order.olast_action = "created"
                order.save()
            elif instance.action_type == "updated":
                order = get_object_or_404(OrderModel, id=instance.object_id)
                shadow = get_object_or_404(
                    ShadowOrderModel, id=instance.shadow_object_id
                )
                order.company = shadow.company
                order.phone_number = shadow.phone_number
                order.banner = shadow.banner
                order.banner_side = shadow.banner_side
                order.rent_price = shadow.rent_price
                order.start_date = shadow.start_date
                order.end_date = shadow.end_date
                order.order_status = shadow.order_status
                order.order_note = shadow.order_note
                order.paid_payment = shadow.paid_payment
                order.olast_action = shadow.olast_action
                order.save()
                shadow.delete()
        elif instance.object_model == "payment_model":
            if instance.action_type == "created":
                payment = get_object_or_404(PaymentModel, id=instance.object_id)
                client = payment.client
                if client.full_payment - client.paid_payment < payment.payment_amount:
                    return JsonResponse(
                        {
                            "success": False,
                            "error_message": "Payment amount cannot exceed the remaining balance of the order.",
                        },
                        status=400,
                    )
                else:
                    client.paid_payment = client.paid_payment - payment.payment_amount
                    client.save()
                    payment.delete()
            elif instance.action_type == "deleted":
                payment = get_object_or_404(PaymentModel, id=instance.object_id)
                payment.plast_action = "created"
                client = payment.client
                if client.full_payment - client.paid_payment < payment.payment_amount:
                    return JsonResponse(
                        {
                            "success": False,
                            "error_message": "Payment amount cannot exceed the remaining balance of the order.",
                        },
                        status=400,
                    )
                else:
                    client.paid_payment = client.paid_payment + payment.payment_amount
                    client.save()
                    payment.save()
            elif instance.action_type == "updated":
                payment = get_object_or_404(PaymentModel, id=instance.object_id)
                shadow = get_object_or_404(
                    ShadowPaymentModel, id=instance.shadow_object_id
                )
                pclient = payment.client
                sclient = shadow.client
                if sclient.full_payment - sclient.paid_payment < shadow.payment_amount:
                    return JsonResponse(
                        {
                            "success": False,
                            "error_message": "Payment amount cannot exceed the remaining balance of the order.",
                        },
                        status=400,
                    )
                elif pclient.paid_payment < payment.payment_amount:
                    return JsonResponse(
                        {
                            "success": False,
                            "error_message": "Payment amount cannot be less than the paid balance of the order.",
                        },
                        status=400,
                    )
                else:
                    x = pclient.paid_payment - payment.payment_amount
                    pclient.paid_payment = x
                    y = (
                        sclient.paid_payment
                        + shadow.payment_amount
                        - payment.payment_amount
                    )
                    sclient.paid_payment = y
                    payment.client = shadow.client
                    payment.payment_amount = shadow.payment_amount
                    payment.plast_action = shadow.plast_action

                    pclient.save()
                    sclient.save()
                    payment.save()
                    shadow.delete()
        elif instance.object_model == "outlay_model":
            if instance.action_type == "created":
                outlay = get_object_or_404(OutlayModel, id=instance.object_id)
                outlay.delete()
            elif instance.action_type == "updated":
                outlay = get_object_or_404(OutlayModel, id=instance.object_id)
                shadow = get_object_or_404(
                    ShadowOutlayModel, id=instance.shadow_object_id
                )
                outlay.outlay_amount = shadow.outlay_amount
                outlay.elast_action = shadow.elast_action
                outlay.save()
                shadow.delete()
            elif instance.action_type == "deleted":
                outlay = get_object_or_404(OutlayModel, id=instance.object_id)
                outlay.elast_action = "created"
                outlay.save()

        elif instance.object_model == "bruh_model":
            if instance.action_type == "created":
                bruh = get_object_or_404(BruhModel, id=instance.object_id)
                bruh.delete()
            elif instance.action_type == "deleted":
                bruh = get_object_or_404(BruhModel, id=instance.object_id)
                bruh.slast_action = "created"
                bruh.save()
            elif instance.action_type == "updated":
                bruh = get_object_or_404(BruhModel, id=instance.object_id)
                shadow = get_object_or_404(
                    ShadowBruhModel, id=instance.shadow_object_id
                )
                bruh.name = shadow.name
                bruh.number = shadow.number
                bruh.rent_price = shadow.rent_price
                bruh.start_date = shadow.start_date
                bruh.end_date = shadow.end_date
                bruh.bruh_note = shadow.bruh_note
                bruh.paid_payment = shadow.paid_payment
                bruh.slast_action = shadow.slast_action
                bruh.save()
                bruh.full_payment = bruh.monthly_payment() * bruh.rent_price
                bruh.save()

                shadow.delete()

        return super().perform_destroy(instance)

    def get_permissions(self):
        permission_classes = [permissions.IsAuthenticated, IsAdminPermission]
        if (
            self.action == "update"
            or self.action == "create"
            or self.action == "partial_update"
        ):
            permission_classes = [permissions.IsAuthenticated, CanNotBePerformed]

        return [permission() for permission in permission_classes]


def ad1(oid, uid, mnum, at):
    x = [
        "user_model",
        "banner_model",
        "order_model",
        "payment_model",
        "outlay_model",
        "bruh_model",
    ][int(mnum) - 1]
    new_action = ActionLogModel.objects.create(
        user_id=uid,
        object_model=x,
        object_id=oid,
        shadow_object_id=None,
        action_type=at,
    )
    if new_action:
        return True
    return False
