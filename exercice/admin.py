from django.contrib import admin
from .models import ExerciseModule, Exercise, ExerciseSubmission

@admin.register(ExerciseModule)
class ExerciseModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'icon')


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'exercise_id', 'difficulty')
    list_filter = ('module', 'difficulty')


@admin.register(ExerciseSubmission)
class ExerciseSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'exercise', 'status', 'submitted_at')
    list_filter = ('status', 'exercise__module')
    search_fields = ('student__username', 'exercise__title')
    
    # Action personnalisée pour valider rapidement les exercices sélectionnés
    actions = ['mark_as_validated']

    @admin.action(description='Valider les exercices sélectionnés 🎉')
    def mark_as_validated(self, request, queryset):
        updated = queryset.update(status='validated')
        self.message_user(request, f"{updated} exercice(s) ont été validés avec succès.")