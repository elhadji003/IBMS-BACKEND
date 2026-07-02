from django.db.models import Prefetch
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import Course, CourseProgress
from ..serializers.courses_serializers import CourseSerializer


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
        queryset = Course.objects.all().order_by("-is_foundational", "title")
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category__iexact=category)

        # 🌟 CORRIGÉ : le serializer attend un attribut "user_progress_list"
        # préchargé sur chaque Course (voir CourseSerializer._get_progress_obj).
        # Sans ce prefetch, il retombait toujours sur None -> valeurs par défaut
        # (time_remaining=3600, is_quiz_unlocked=False) même après le délai écoulé.
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


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    - GET    : Détail d'un cours via son ID (Tout utilisateur connecté)
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
        # 🌟 CORRIGÉ : même prefetch que CourseListView, indispensable ici aussi
        # car c'est CourseDetailView qui sert la page CoursDetail.jsx (le chrono).
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


class UpdateCourseProgressView(APIView):
    """
    Crée ou met à jour la progression de l'utilisateur connecté via PATCH.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"detail": "Cours introuvable."}, status=status.HTTP_404_NOT_FOUND)

        # Sécurité Débutant optionnelle : bloque si le cours d'intro n'est pas fini
        if not course.is_foundational:
            intro_done = CourseProgress.objects.filter(
                user=request.user, course__is_foundational=True, is_completed=True
            ).exists()
            if not intro_done:
                return Response(
                    {"detail": "Action interdite. Terminez d'abord le cours d'introduction."},
                    status=status.HTTP_403_FORBIDDEN
                )

        progress_percentage = request.data.get("progress_percentage")
        if progress_percentage is None:
            return Response({"detail": "Le champ 'progress_percentage' est requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            progress_percentage = int(progress_percentage)
        except (TypeError, ValueError):
            return Response({"detail": "'progress_percentage' doit être un entier."}, status=status.HTTP_400_BAD_REQUEST)

        if not (0 <= progress_percentage <= 100):
            return Response({"detail": "'progress_percentage' doit être entre 0 et 100."}, status=status.HTTP_400_BAD_REQUEST)

        progress, _created = CourseProgress.objects.get_or_create(user=request.user, course=course)

        # 🌟 CORRIGÉ : garde-fou anti-triche.
        # On ne peut pas passer à 100% (compléter le cours) sans que le quiz
        # ait réellement été débloqué côté serveur (chrono écoulé + logique métier
        # de CourseProgress.is_quiz_unlocked). Ça bloque un PATCH direct via devtools
        # qui tenterait de sauter l'étape du quiz.
        if progress_percentage >= 100 and not progress.is_quiz_unlocked:
            return Response(
                {"detail": "Impossible de valider le cours : le quiz n'est pas encore débloqué."},
                status=status.HTTP_403_FORBIDDEN
            )

        progress.progress_percentage = progress_percentage
        progress.is_completed = progress_percentage >= 100
        progress.save()

        return Response({
            "course_id": course.id,
            "progress_percentage": progress.progress_percentage,
            "is_completed": progress.is_completed,
        }, status=status.HTTP_200_OK)