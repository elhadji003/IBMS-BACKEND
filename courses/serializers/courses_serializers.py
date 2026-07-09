from django.utils import timezone
from rest_framework import serializers
from ..models import Course, CourseProgress

class CourseSerializer(serializers.ModelSerializer):
    is_locked = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()
    is_quiz_unlocked = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', "slug", 'description', 'category', 'is_free', 'price',
            'image_url', 'is_foundational', 'is_locked', 
            'user_progress', 'time_remaining', 'is_quiz_unlocked'
        ]

    def _get_progress_obj(self, obj):
        """
        Récupère le progrès préchargé (optimisation) ou fallback BDD.
        """
        request = self.context.get('request')
        if not request or not request.user or request.user.is_anonymous:
            return None

        # 1. Tenter d'utiliser la liste préchargée optimisée du ViewSet
        progress_list = getattr(obj, 'user_progress_list', [])
        if progress_list:
            return progress_list[0]

        # 2. Fallback BDD
        return CourseProgress.objects.filter(user=request.user, course=obj).first()

    def get_is_locked(self, obj):
        request = self.context.get('request')
        if not request or not request.user or request.user.is_anonymous:
            return True

        if obj.is_foundational:
            return False
            
        # Utilisation sécurisée du cache de contexte par requête
        if 'foundational_completed' not in self.context:
            self.context['foundational_completed'] = CourseProgress.objects.filter(
                user=request.user, 
                course__is_foundational=True, 
                is_completed=True
            ).exists()

        return not self.context['foundational_completed']

    def get_user_progress(self, obj):
        progress = self._get_progress_obj(obj)
        return progress.progress_percentage if progress else 0

    def get_time_remaining(self, obj):
        progress = self._get_progress_obj(obj)
        
        if not progress:
            return 120
        
        # On appelle directement la propriété dynamique du modèle
        return progress.time_remaining

    def get_is_quiz_unlocked(self, obj):
        progress = self._get_progress_obj(obj)
        if not progress:
            return False
            
        # On appelle directement la propriété du modèle
        return progress.is_quiz_unlocked