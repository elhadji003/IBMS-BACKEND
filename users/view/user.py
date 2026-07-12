from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.pagination import PageNumberPagination

# Récupération dynamique de ton modèle Utilisateur (Custom ou natif)
User = get_user_model()

class AdminUserPagination(PageNumberPagination):
    """Configuration de la pagination pour les administrateurs"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class AllUsersView(APIView):
    # Sécurité : Seuls les utilisateurs connectés avec le statut Admin (is_staff=True) y ont accès
    permission_classes = [IsAdminUser]

    def get(self, request):
        """
        1. GET ALL USERS (Accès global)
        URL cible côté React : users/admin/?page=X
        """
        try:
            # Récupère tous les utilisateurs, classés du plus récent au plus ancien
            users = User.objects.all().order_by('-created_at')
            
            # Application de la pagination standard
            paginator = AdminUserPagination()
            page = paginator.paginate_queryset(users, request, view=self)
            
            # Sérialisation à plat des données utilisateurs
            user_list = []
            target_set = page if page is not None else users
            
            for user in target_set:
                user_list.append({
                    "id": user.id,
                    "email": user.email,
                    "first_name": getattr(user, 'first_name', ''),
                    "last_name": getattr(user, 'last_name', ''),
                    "is_active": user.is_active,
                    "is_staff": user.is_staff,
                    "created_at": user.created_at.strftime("%d/%m/%Y à %H:%M") if user.created_at else None
                })
            
            # Retourne la réponse paginée si elle est active, sinon la liste brute
            if page is not None:
                return paginator.get_paginated_response(user_list)
                
            return Response(user_list, status=status.HTTP_OK)
            
        except Exception as e:
            return Response(
                {"detail": f"Erreur lors de la récupération : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def patch(self, request):
        """
        2. UPDATE TOGGLE STATUS (Modification partielle)
        URL cible côté React : users/admin/  (avec id et is_active dans le body JSON)
        """
        user_id = request.data.get('id')
        is_active_status = request.data.get('is_active')

        if user_id is None or is_active_status is None:
            return Response(
                {"detail": "Les champs 'id' et 'is_active' sont obligatoires dans le corps de la requête."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        target_user = get_object_or_404(User, id=user_id)
        
        # Sécurité : L'admin ne doit pas pouvoir se bloquer lui-même
        if target_user == request.user and is_active_status is False:
            return Response(
                {"detail": "Action impossible : vous ne pouvez pas suspendre votre propre compte."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            target_user.is_active = bool(is_active_status)
            target_user.save()
            
            statut_texte = "activé" if target_user.is_active else "suspendu"
            return Response(
                {
                    "detail": f"Le compte de l'utilisateur a été {statut_texte} avec succès.",
                    "is_active": target_user.is_active
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detail": f"Erreur lors du changement de statut : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request):
        """
        3. DELETE USER (Suppression définitive)
        URL cible côté React : users/admin/?id=X
        """
        user_id = request.query_params.get('id')
        
        if not user_id:
            return Response(
                {"detail": "L'identifiant (id) de l'utilisateur est requis en paramètre d'URL."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user_to_delete = get_object_or_404(User, id=user_id)
        
        # Sécurité : L'admin ne doit pas pouvoir s'auto-détruire
        if user_to_delete == request.user:
            return Response(
                {"detail": "Action impossible : vous ne pouvez pas supprimer votre propre compte."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            user_to_delete.delete()
            return Response(
                {"detail": "L'utilisateur a été supprimé de la base de données."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detail": f"Erreur lors de la suppression : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            

class UserCountView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "total_users": User.objects.count(),
            "active_users": User.objects.filter(is_active=True).count(),
            "inactive_users": User.objects.filter(is_active=False).count(),
            # Remplacez 'admin' par la valeur exacte utilisée dans votre projet :
            "admin_users": User.objects.filter(role='super-admin').count(), 
        })