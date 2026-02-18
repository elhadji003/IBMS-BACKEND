from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Course, CoursePayment
from .serializers.cours import CourseSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models.cours_content import CourseContent
from .serializers.cours_content import CourseContentSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [permissions.IsAdminUser()]
        if self.action in ["pay", "my_courses"]:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    @action(detail=False, methods=["get"], url_path="my-courses")
    def my_courses(self, request):
        payments = CoursePayment.objects.filter(
            user=request.user,
            status="paid"
        ).select_related("course")

        courses = [p.course for p in payments]

        serializer = self.get_serializer(
            courses,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=["post"])
    def pay(self, request, pk=None):
        course = self.get_object()
        user = request.user

        # 1. Créer la transaction dans ta base
        payment = CoursePayment.objects.create(
            user=user,
            course=course,
            amount=course.price,
            status="pending"
        )

        # 2. Paramètres demandés par TouchPay (Gutouch)
        # Note: Ces noms de variables dépendent de leur version d'API
        params = {
            "id_partenaire": "VOTRE_ID_PARTENAIRE",
            "id_service": "VOTRE_ID_SERVICE", # Ex: Wave ou OrangeMoney
            "montant": int(course.price),
            "id_transaction": payment.transaction_ref,
            "callback_url": "http://localhost:5173/user/cours/1/",
            "nom_client": user.username,
            "description": f"Achat du cours : {course.title}"
        }

        # 3. Construire l'URL de redirection
        # Chez TouchPay, on redirige souvent vers leur page de paiement avec les paramètres
        base_url = "https://touchpay.gutouch.net/touchpayv2/pay/"
        
        # On retourne l'URL au Frontend (React/Flutter/Vue)
        return Response({
            "payment_url": f"{base_url}?id_partenaire={params['id_partenaire']}&montant={params['montant']}&id_transaction={params['id_transaction']}...",
            "transaction_ref": payment.transaction_ref
        })



class CourseContentViewSet(ModelViewSet):
    serializer_class = CourseContentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CourseContent.objects.all()

        course_id = self.request.query_params.get("course")
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        return queryset
