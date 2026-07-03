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
            'id', 'title', 'slug', 'description', 'category', 'is_free', 'price',
            'image_url', 'is_foundational', 'is_locked', 
            'user_progress', 'time_remaining', 'is_quiz_unlocked'
        ]

    def _get_progress_obj(self, obj):
        """
        Méthode utilitaire interne pour récupérer le progrès préchargé 
        sans refaire de requête SQL.
        """
        # Si la liste préchargée existe (grâce au prefetch_related)
        progress_list = getattr(obj, 'user_progress_list', [])
        return progress_list[0] if progress_list else None

    def get_is_locked(self, obj):
        user = self.context['request'].user
        if not user or user.is_anonymous:
            return True

        if obj.is_foundational:
            return False
            
        # Optimisation : On stocke le résultat dans le contexte de la requête 
        # pour éviter de réexécuter cette requête globale pour chaque cours.
        if 'foundational_completed' not in self.context:
            self.context['foundational_completed'] = CourseProgress.objects.filter(
                user=user, 
                course__is_foundational=True, 
                is_completed=True
            ).exists()

        return not self.context['foundational_completed']

    def get_user_progress(self, obj):
        progress = self._get_progress_obj(obj)
        return progress.progress_percentage if progress else 0

    def get_time_remaining(self, obj):
        progress = self._get_progress_obj(obj)
        return progress.time_remaining if progress else 3600

    def get_is_quiz_unlocked(self, obj):
        progress = self._get_progress_obj(obj)
        return progress.is_quiz_unlocked if progress else False