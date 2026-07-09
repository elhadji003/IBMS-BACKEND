from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMultiAlternatives
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
import os
from django.contrib.auth.password_validation import validate_password
from django.conf import settings

User = get_user_model()

class RequestPasswordResetView(APIView):
    def post(self, request):
        email = request.data.get("email")
        user = User.objects.filter(email=email).first()

        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)

            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
            # Modification ici pour matcher la structure exacte de la route React
            reset_link = f"{frontend_url}/reset/password/{uid}/{token}"

            context = {
                "user_first_name": user.first_name or "",
                "reset_link": reset_link,
                "app_name": "LearnTech",
            }

            html = render_to_string("emails/password_reset_email.html", context)
            text = render_to_string("emails/password_reset_email.txt", context)

            email_message = EmailMultiAlternatives(
                subject="Réinitialisation de mot de passe",
                body=text,
                from_email=settings.DEFAULT_FROM_EMAIL,  # <-- AJOUTE CETTE LIGNE ICI
                to=[user.email],
            )
            email_message.attach_alternative(html, "text/html")
            email_message.send()

        # Remplacement de "message" par "detail" pour la cohérence avec Sonner
        return Response({
            "detail": "Si un compte existe, un email de réinitialisation a été envoyé."
        }, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    # Remplacement de uidb64 par uid dans la signature pour correspondre au front
    def post(self, request, uid, token):
        try:
            uid_decoded = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid_decoded)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({"detail": "Le lien est invalide ou a expiré."}, status=status.HTTP_400_BAD_REQUEST)

            new_password = request.data.get("new_password")

            if not new_password:
                return Response({"detail": "Le mot de passe est obligatoire."}, status=status.HTTP_400_BAD_REQUEST)

            # Validation des règles de mot de passe de Django (longueur, complexité...)
            try:
                validate_password(new_password, user)
            except Exception as e:
                # Renvoie les erreurs de validation de Django (ex: trop commun, trop court...)
                return Response({"detail": list(e.messages)[0]}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()

            return Response({"detail": "Mot de passe réinitialisé avec succès."}, status=status.HTTP_200_OK)

        except Exception:
            return Response({"detail": "Le lien est invalide ou a expiré."}, status=status.HTTP_400_BAD_REQUEST)    