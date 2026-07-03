import hashlib
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.conf import settings

from ..models import Payment
from courses.models import CourseProgress

@csrf_exempt
def paydunya_callback(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    # 1. Récupération des données brutes de PayDunya
    if request.content_type == "application/json":
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    else:
        payload = request.POST

    # 2. Extraction des blocs imbriqués propres à PayDunya
    # PayDunya envoie un dictionnaire imbriqué sous la clé 'data'
    invoice_data = payload.get("data", {}) if isinstance(payload, dict) else payload
    
    token = invoice_data.get("token")
    status_paydunya = invoice_data.get("status")
    hash_recu = payload.get("hash")

    # 3. Sécurité : Vérification stricte de la signature SHA-512
    # PayDunya calcule le SHA512 de la concaténation de la string reçue ou de la Master Key brute
    hash_attendu = hashlib.sha512(settings.PAYDUNYA_MASTER_KEY.encode()).hexdigest()
    if hash_recu != hash_attendu:
        return JsonResponse({"error": "Invalid signature"}, status=403)

    if not token:
        return JsonResponse({"error": "Missing token"}, status=400)

    # 4. Récupération et mise à jour du paiement local
    payment = get_object_or_404(Payment, paydunya_invoice_token=token)

    # Note : Le statut renvoyé par PayDunya est généralement "completed"
    if status_paydunya == "completed":
        payment.status = Payment.Status.PAID
        payment.save()

        # Débloquer le cours (CourseProgress) pour l'étudiant
        CourseProgress.objects.get_or_create(
            user=payment.user,
            course=payment.course
        )
    elif status_paydunya in ["cancelled", "failed"]:
        payment.status = Payment.Status.FAILED
        payment.save()
    else:
        # Si c'est un statut intermédiaire (ex: pending), on ne fait rien mais on répond 200
        pass

    return JsonResponse({"status": "success"})