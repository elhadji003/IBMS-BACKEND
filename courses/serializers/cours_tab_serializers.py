from rest_framework import serializers
from ..models import Course, CourseProgress

class CourseTabSerializer(serializers.ModelSerializer):
    is_locked = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'category', 'is_locked']
        
    def get_is_locked(self, obj):  # Remis au bon niveau d'indentation
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