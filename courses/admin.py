from django.contrib import admin
from .models import Course, CourseProgress, Question, Choice, QuizSubmission

# --- Tes configurations existantes (Course et CourseProgress) ---

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_foundational', 'created_at')
    list_filter = ('category', 'is_foundational')
    search_fields = ('title', 'description', 'category')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):
    list_display = ('get_user_email', 'get_course_title', 'progress_percentage', 'is_completed', 'updated_at')
    list_filter = ('is_completed', 'course__category')
    search_fields = ('user__email', 'course__title')
    raw_id_fields = ('user', 'course')

    @admin.display(ordering='user__email', description='Étudiant (Email)')
    def get_user_email(self, obj):
        return obj.user.email

    @admin.display(ordering='course__title', description='Cours')
    def get_course_title(self, obj):
        return obj.course.title


# --- 🎯 NOUVELLE CONFIGURATION : SYSTÈME DE QUIZZ INTERACTIF ---

class ChoiceInline(admin.TabularInline):
    """Permet d'ajouter les choix directement sous la question (en tableau)"""
    model = Choice
    extra = 3  # Affiche par défaut 3 lignes de réponses vides prêtes à être remplies
    max_num = 6  # Maximum 6 choix par question


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Panel pour gérer les questions"""
    list_display = ('text', 'get_course_title')
    list_filter = ('course',)
    search_fields = ('text', 'course__title')
    
    # 🌟 Magie : On intègre les choix directement dans l'édition de la question !
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
    readonly_fields = ('user', 'course', 'score', 'passed', 'created_at') # Empêche la modification des notes à la main

    @admin.display(ordering='user__email', description='Étudiant')
    def get_user_email(self, obj):
        return obj.user.email

    @admin.display(ordering='course__title', description='Cours')
    def get_course_title(self, obj):
        return obj.course.title