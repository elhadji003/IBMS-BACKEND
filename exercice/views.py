from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ExerciseModule, Exercise, ExerciseSubmission
from .serializers import ExerciseModuleSerializer, ExerciseSubmissionSerializer # On va créer ce serializer
from notification.models import Notification
class ExerciseModuleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ExerciseModuleSerializer

    def get_queryset(self):
        return ExerciseModule.objects.all().prefetch_related('exercises')

    # --- NOUVEL ENDPOINT POUR L'ADMIN ---
    @action(detail=False, methods=['get'], url_path='all-submissions')
    def all_submissions(self, request):
        """
        Renvoie toutes les soumissions en attente de validation (réservé aux admins)
        """
        if not request.user.is_staff and not request.user.is_superuser:
            return Response({"detail": "Accès interdit."}, status=status.HTTP_403_FORBIDDEN)
            
        submissions = ExerciseSubmission.objects.filter(status='pending').select_related('student', 'exercise')
        
        
        
        # Formatage simple et rapide des données à renvoyer
        data = [{
            "id": sub.id,
            "student_id": sub.student.id,
            "student_username": sub.student.first_name, # Ajuste selon ton champ (ex: get_full_name())
            "exercise_id": sub.exercise.id,
            "exercise_title": sub.exercise.title,
            "exercise_num": sub.exercise.exercise_id,
            "status": sub.status,
            "submitted_at": sub.submitted_at
        } for sub in submissions]
        
        return Response(data, status=status.HTTP_200_OK)

    # --- AJUSTEMENT DE TON ACTION DE VALIDATION ---
    @action(detail=False, methods=['post'], url_path='update-status')
    def update_status(self, request):
        exercise_id = request.data.get('exercise_id')
        new_status = request.data.get('status')
        student_id = request.data.get('student_id') # L'admin envoie l'ID de l'étudiant concerné

        if not exercise_id or not new_status:
            return Response({"error": "Champs requis manquants."}, status=status.HTTP_400_BAD_REQUEST)

        # Si l'admin valide, on cible l'étudiant concerné, sinon c'est l'étudiant connecté
        target_user = request.user
        if (request.user.is_staff or request.user.is_superuser) and student_id:
            from django.contrib.auth import get_user_model
            target_user = get_user_model().objects.get(id=student_id)

        submission, created = ExerciseSubmission.objects.get_or_create(
            student=target_user,
            exercise_id=exercise_id,
            defaults={'status': new_status}
        )

        if not created:
            submission.status = new_status
            submission.save()
            
        # ==========================================================
        # LOGIQUE DE NOTIFICATION : Si l'admin valide l'exercice
        # ==========================================================
        if new_status == 'validated' and (request.user.is_staff or request.user.is_superuser):
            exercise = Exercise.objects.get(id=exercise_id)
            Notification.objects.create(
                user=target_user, # L'étudiant reçoit la notification
                title="🎉 Exercice Validé !",
                message=f"Félicitations ! Votre travail pour l'atelier '{exercise.title}' a été validé par l'équipe pédagogique."
            )

        return Response({"status": submission.status}, status=status.HTTP_200_OK)