from django.db.models import Prefetch
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import Course, CourseProgress
from ..serializers.courses_serializers import CourseSerializer
from ..serializers.cours_tab_serializers import CourseTabSerializer

User = get_user_model()

class CourseListView(generics.ListCreateAPIView):
    """
    - GET  : Liste tous les cours (Accessible par tout utilisateur connecté)
    - POST : Crée un cours (Accessible par l'Admin uniquement)
    """
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Course.objects.all().order_by("-is_foundational", "id")
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category__iexact=category)

        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.prefetch_related(
                Prefetch(
                    "user_progress",
                    queryset=CourseProgress.objects.filter(user=user),
                    to_attr="user_progress_list",
                )
            )
        return queryset
    
class CourseTabListView(generics.ListAPIView):
    """Endpoint léger : Liste uniquement l'essentiel pour les onglets"""
    permission_classes = [IsAuthenticated] # Ajustez selon vos besoins
    serializer_class = CourseTabSerializer

    def get_queryset(self):
        return Course.objects.all().order_by('id')
    
class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    - GET    : Détail d'un cours + Initialisation automatique de la progression (F5 proof)
    - PUT    : Modification complète (Admin uniquement)
    - PATCH  : Modification partielle (Admin uniquement)
    - DELETE : Suppression d'un cours (Admin uniquement)
    """
    serializer_class = CourseSerializer
    lookup_field = "pk"
    lookup_url_kwarg = "course_id"

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Course.objects.all()
        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.prefetch_related(
                Prefetch(
                    "user_progress",
                    queryset=CourseProgress.objects.filter(user=user),
                    to_attr="user_progress_list",
                )
            )
        return queryset

    def retrieve(self, request, *args, **kwargs):
        """
        Surcharge du GET pour garantir la création du CourseProgress dès l'entrée du cours.
        """
        instance = self.get_object()
        user = request.user

        if user.is_authenticated:
            # Sécurité F5 : On s'assure que le CourseProgress existe dès qu'on demande le détail
            progress, created = CourseProgress.objects.get_or_create(
                user=user,
                course=instance
            )
            # On met à jour l'attribut préchargé pour que le sérialiseur l'utilise immédiatement
            instance.user_progress_list = [progress]

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class UpdateCourseProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"detail": "Cours introuvable."}, status=status.HTTP_404_NOT_FOUND)

        # 1. Vérification du cours de fondation
        if not course.is_foundational:
            intro_done = CourseProgress.objects.filter(
                user=request.user, course__is_foundational=True, is_completed=True
            ).exists()
            if not intro_done:
                return Response(
                    {"detail": "Action interdite. Terminez d'abord le cours d'introduction."},
                    status=status.HTTP_403_FORBIDDEN
                )

        # 2. Validation des inputs
        progress_percentage = request.data.get("progress_percentage")
        if progress_percentage is None:
            return Response({"detail": "Le champ 'progress_percentage' est requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            progress_percentage = int(progress_percentage)
        except (TypeError, ValueError):
            return Response({"detail": "'progress_percentage' doit être un entier."}, status=status.HTTP_400_BAD_REQUEST)

        if not (0 <= progress_percentage <= 100):
            return Response({"detail": "'progress_percentage' doit être entre 0 et 100."}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Récupération (il existe forcément déjà grâce au CourseDetailView)
        progress, created = CourseProgress.objects.get_or_create(
            user=request.user, 
            course=course
        )
        
        # 4. SÉCURITÉ CRITIQUE UNIFIÉE
        if progress_percentage >= 100 and not progress.is_quiz_unlocked:
            return Response(
                {"detail": "Impossible de valider le cours : le quiz n'est pas encore débloqué."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 5. Application des changements
        progress.progress_percentage = progress_percentage
        progress.is_completed = progress_percentage >= 100
        progress.save()

        # Injection pour le sérialiseur
        course.user_progress_list = [progress]
        serializer = CourseSerializer(course, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserCourseStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.query_params.get('id')
        target_user = request.user
        
        if user_id:
            if request.user.is_superuser or getattr(request.user, 'is_staff', False):
                target_user = get_object_or_404(User, id=user_id)
            else:
                return Response(
                    {"detail": "Accès refusé. Seul un administrateur peut voir les statistiques d'un autre utilisateur."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        completed_courses_count = CourseProgress.objects.filter(
            user=target_user, 
            is_completed=True
        ).count()
        
        total_courses_count = Course.objects.count()

        return Response({
            "user_id": target_user.id,
            "completed_courses": completed_courses_count,
            "total_courses": total_courses_count,
            "completion_percentage": (
                round((completed_courses_count / total_courses_count) * 100, 2) 
                if total_courses_count > 0 else 0
            )
        }, status=status.HTTP_200_OK)
        
        
class CoursCountView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            "total_cours": Course.objects.count()
        })