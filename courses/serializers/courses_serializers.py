from rest_framework import serializers
from ..models import Course, CourseProgress

class CourseSerializer(serializers.ModelSerializer):
    is_locked = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'slug', 'description', 'category', 'image_url', 'is_foundational', 'is_locked', 'user_progress']

    def get_is_locked(self, obj):
        user = self.context['request'].user
        
        # Si le cours lui-même est le cours de fondation, il n'est jamais bloqué
        if obj.is_foundational:
            return False
            
        # On vérifie si l'utilisateur a complété le cours de fondation
        foundational_course_completed = CourseProgress.objects.filter(
            user=user, 
            course__is_foundational=True, 
            is_completed=True
        ).exists()

        # Si le cours de fondation n'est pas terminé, ce cours de spécialisation est bloqué
        return not foundational_course_completed

    def get_user_progress(self, obj):
        user = self.context['request'].user
        try:
            progress = CourseProgress.objects.get(user=user, course=obj)
            return progress.progress_percentage
        except CourseProgress.DoesNotExist:
            return 0