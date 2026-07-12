from django.contrib import admin
from .models import Exercise, ExerciseSubmission
from notification.models import Notification

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    # Remplacement de 'module' par 'course'
    list_display = ('exercise_id', 'title', 'course', 'difficulty')
    list_filter = ('course', 'difficulty')
    search_fields = ('title', 'course__title')
    ordering = ('course', 'exercise_id')


@admin.register(ExerciseSubmission)
class ExerciseSubmissionAdmin(admin.ModelAdmin):
    # Remplacement de 'exercise__module' par 'exercise__course'
    list_display = ('student', 'exercise', 'status', 'submitted_at')
    list_filter = ('status', 'exercise__course')
    search_fields = ('student__username', 'student__first_name', 'exercise__title')
    
    actions = ['mark_as_validated']

    @admin.action(description='Valider les exercices sélectionnés 🎉')
    def mark_as_validated(self, request, queryset):
        # Pour déclencher les notifications, on boucle sur les soumissions ciblées
        count = 0
        for submission in queryset.exclude(status='validated'):
            submission.status = 'validated'
            submission.save()
            
            # Déclenchement de la notification à l'étudiant
            Notification.objects.create(
                user=submission.student,
                title="🎉 Exercice Validé !",
                message=f"Félicitations ! Votre travail pour l'atelier '{submission.exercise.title}' a été validé par l'équipe pédagogique."
            )
            count += 1
            
        self.message_user(request, f"{count} exercice(s) ont été validés et les étudiants ont été notifiés.")