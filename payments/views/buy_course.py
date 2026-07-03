from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from ..models import Payment
from courses.models import Course, CourseProgress
from ..paydunya_service import create_paydunya_invoice

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def buy_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if course.is_free:
        CourseProgress.objects.get_or_create(user=request.user, course=course)
        return Response({"message": "Free course unlocked"})

    # Anti-doublon amélioré
    existing = Payment.objects.filter(
        user=request.user,
        course=course,
        status__in=[Payment.Status.PENDING, Payment.Status.PAID]
    ).first()

    if existing:
        if existing.status == Payment.Status.PAID:
            return Response({"message": "Already enrolled"})
        
        # S'il est PENDING mais possède une URL valide, on la renvoie
        if existing.paydunya_url:
            return Response({"payment_url": existing.paydunya_url})
        
        # Si l'URL était nulle/foireuse, on invalide l'ancien pour en recréer un propre
        existing.status = Payment.Status.FAILED
        existing.save()

    # Création du paiement local
    payment = Payment.objects.create(
        user=request.user,
        course=course,
        amount=course.price
    )

    # Appel de ton service PayDunya
    result = create_paydunya_invoice(payment)

    if result["success"]:
        token = result["token"]
        real_payment_url = result["url"]  # ✨ On prend DIRECTEMENT la bonne URL du service !
        
        # Sauvegarde des bonnes infos clean en BDD
        payment.paydunya_invoice_token = token
        payment.paydunya_url = real_payment_url
        payment.save()
        
        # Renvoie la clé attendue par ton front-end
        return Response({
            "status": "success",
            "payment_url": real_payment_url
        }, status=status.HTTP_200_OK)

    # En cas d'échec de la création de facture PayDunya
    payment.status = Payment.Status.FAILED
    payment.save()
    
    return Response(
        {"error": result.get("error", "Payment failed")}, 
        status=status.HTTP_400_BAD_REQUEST
    )