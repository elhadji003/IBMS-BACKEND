from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from ..serializers.register_user import RegisterUserSerializer
from ..serializers.login_user import MyTokenObtainPairSerializer
from django.contrib.auth import logout

class RegisterUserView(APIView):
    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            return Response({
                    "message": "Utilisateur créé avec succés",
                    "user": {
                        "id": user.id,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "email": user.email,
                        "phone": user.phone_number,
                        "role": user.role,
                    },
            },
            status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class LoginUserView(APIView):
    def post(self, request):
        serializer = MyTokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"detail": "Déjà déconnecté"},
                status=status.HTTP_204_NO_CONTENT
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            pass

        return Response(
            {"detail": "Déconnecté"},
            status=status.HTTP_205_RESET_CONTENT
        )
