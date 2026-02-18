from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers.profile_user import ProfileUserSerializer
from django.contrib.auth import authenticate

# ----- Recupérer le Profile du User ----
class GetProfileUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileUserSerializer(
            request.user,
            context={"request": request}
        )
        return Response(serializer.data)

# ----- Recupérer le Profile du User Par ID -----
class GetProfileUserByIdView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = request.user.__class__.objects.get(id=user_id)
        except request.user.__class__.DoesNotExist:
            return Response(
                {"error": "Utilisateur non trouvé"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProfileUserSerializer(
            user,
            context={"request": request}
        )
        return Response(serializer.data)

# ----- Modifier le Profile du User -----
class UpdateProfileUserView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = ProfileUserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ----- Supprimer le Compte du User -----
class DeleteAccountWithPwd(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        password = request.data.get("password")

        if not password:
            return Response(
                {"error": "Mot de passe requis"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(
            email=request.user.email,
            password=password
        )

        if not user:
            return Response(
                {"error": "Mot de passe incorrect"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        request.user.delete()
        return Response(
            {"message": "Compte supprimé définitivement"},
            status=status.HTTP_200_OK
        )