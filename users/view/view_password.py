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

User = get_user_model()

class RequestPasswordResetView(APIView):
    def post(self, request):
        email = request.data.get("email")
        user = User.objects.filter(email=email).first()

        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)

            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
            reset_link = f"{frontend_url}/reset/password/{uid}/{token}"
            

            context = {
                "user_first_name": user.first_name or "",
                "reset_link": reset_link,
                "app_name": "IBMS",
            }

            html = render_to_string("emails/password_reset_email.html", context)
            text = render_to_string("emails/password_reset_email.txt", context)

            email_message = EmailMultiAlternatives(
                subject="Réinitialisation de mot de passe",
                body=text,
                to=[user.email],
            )
            email_message.attach_alternative(html, "text/html")
            email_message.send()

        return Response({
            "message": "Si un compte existe, un email a été envoyé."
        })

class PasswordResetConfirmView(APIView):
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({"error": "Lien invalide ou expiré."}, status=400)

            new_password = request.data.get("new_password")
            re_new_password = request.data.get("re_new_password")

            if new_password != re_new_password:
                return Response({"error": "Les mots de passe ne correspondent pas."}, status=400)

            validate_password(new_password, user)

            user.set_password(new_password)
            user.save()

            return Response({"message": "Mot de passe réinitialisé avec succès."})

        except Exception:
            return Response({"error": "Lien invalide ou expiré."}, status=400)
