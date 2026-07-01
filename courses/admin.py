from django.contrib import admin
from .models import Course, CourseProgress, Question, Choice, QuizSubmission

# --- Configurations Course et CourseProgress ---

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_foundational', 'created_at')
    list_filter = ('category', 'is_foundational')
    search_fields = ('title', 'description', 'category')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):
    # 🌟 AJOUT : 'started_at', 'get_time_remaining' et 'get_quiz_unlocked' dans l'affichage
    list_display = (
        'get_user_email', 
        'get_course_title', 
        'progress_percentage', 
        'is_completed', 
        'started_at',           # Heure de début
        'get_time_remaining',   # Temps restant calculé
        'get_quiz_unlocked',    # Statut du quiz
        'updated_at'
    )
    list_filter = ('is_completed', 'course__category')
    search_fields = ('user__email', 'course__title')
    raw_id_fields = ('user', 'course')
    
    # Rend ces champs visibles mais non modifiables lors de l'édition d'une ligne
    readonly_fields = ('started_at', 'get_time_remaining', 'get_quiz_unlocked')

    @admin.display(ordering='user__email', description='Étudiant (Email)')
    def get_user_email(self, obj):
        return obj.user.email

    @admin.display(ordering='course__title', description='Cours')
    def get_course_title(self, obj):
        return obj.course.title

    # 🛠️ Affiche la propriété dynamique 'time_remaining' dans l'admin
    @admin.display(description='Temps Restant (s)')
    def get_time_remaining(self, obj):
        return f"{obj.time_remaining}s"

    # 🛠️ Affiche un indicateur visuel True/False (icône verte/rouge) pour le déblocage
    @admin.display(boolean=True, description='Quiz Débloqué ?')
    def get_quiz_unlocked(self, obj):
        return obj.is_quiz_unlocked


# --- 🎯 SYSTÈME DE QUIZZ INTERACTIF ---

class ChoiceInline(admin.TabularInline):
    """Permet d'ajouter les choix directement sous la question (en tableau)"""
    model = Choice
    extra = 3  
    max_num = 6  


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Panel pour gérer les questions"""
    list_display = ('text', 'get_course_title')
    list_filter = ('course',)
    search_fields = ('text', 'course__title')
    inlines = [ChoiceInline]

    @admin.display(ordering='course__title', description='Cours Associé')
    def get_course_title(self, obj):
        return obj.course.title


@admin.register(QuizSubmission)
class QuizSubmissionAdmin(admin.ModelAdmin):
    """Panel de contrôle pour voir l'historique des notes des élèves"""
    list_display = ('get_user_email', 'get_course_title', 'score', 'passed', 'created_at')
    list_filter = ('passed', 'course')
    search_fields = ('user__email', 'course__title')
    readonly_fields = ('user', 'course', 'score', 'passed', 'created_at') 

    @admin.display(ordering='user__email', description='Étudiant')
    def get_user_email(self, obj):
        return obj.user.email

    @admin.display(ordering='course__title', description='Cours')
    def get_course_title(self, obj):
        return obj.course.title