from rest_framework import serializers
from ..models import Course, CourseProgress

class CourseSerializer(serializers.ModelSerializer):
    is_locked = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()       # Changé en SerializerMethodField
    is_quiz_unlocked = serializers.SerializerMethodField()     # Changé en SerializerMethodField

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'category', 
            'image_url', 'is_foundational', 'is_locked', 
            'user_progress', 'time_remaining', 'is_quiz_unlocked'
        ]

    def get_is_locked(self, obj):
        user = self.context['request'].user
        
        # Si l'utilisateur n'est pas connecté (sécurité)
        if not user or user.is_anonymous:
            return True

        if obj.is_foundational:
            return False
            
        foundational_course_completed = CourseProgress.objects.filter(
            user=user, 
            course__is_foundational=True, 
            is_completed=True
        ).exists()

        return not foundational_course_completed

    def get_user_progress(self, obj):
        user = self.context['request'].user
        if not user or user.is_anonymous:
            return 0
            
        try:
            progress = CourseProgress.objects.get(user=user, course=obj)
            return progress.progress_percentage
        except CourseProgress.DoesNotExist:
            return 0

    def get_time_remaining(self, obj):
        user = self.context['request'].user
        if not user or user.is_anonymous:
            return 60 # Ou le temps par défaut par sécurité

        try:
            progress = CourseProgress.objects.get(user=user, course=obj)
            # On appelle la @property définie dans le modèle CourseProgress
            return progress.time_remaining
        except CourseProgress.DoesNotExist:
            # Si la ligne n'existe pas encore, l'utilisateur n'a pas commencé le cours,
            # donc il lui reste tout le temps (1 heure = 3600 secondes)
            return 60

    def get_is_quiz_unlocked(self, obj):
        user = self.context['request'].user
        if not user or user.is_anonymous:
            return False

        try:
            progress = CourseProgress.objects.get(user=user, course=obj)
            # On appelle la @property définie dans le modèle CourseProgress
            return progress.is_quiz_unlocked
        except CourseProgress.DoesNotExist:
            # S'il n'a pas commencé le cours, le quiz est forcément verrouillé
            return False