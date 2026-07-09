from rest_framework import serializers
from .models import ExerciseModule, Exercise, ExerciseSubmission
from courses.models import CourseProgress

class ExerciseSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = Exercise
        fields = ['id', 'exercise_id', 'title', 'desc', 'difficulty', 'status']

    def get_status(self, obj):
        # Récupère l'utilisateur connecté depuis le contexte de la requête
        user = self.context.get('request').user
        if user and user.is_authenticated:
            submission = ExerciseSubmission.objects.filter(student=user, exercise=obj).first()
            if submission:
                return submission.status
        return 'not_started'


class ExerciseModuleSerializer(serializers.ModelSerializer):
    exercises = ExerciseSerializer(many=True, read_only=True)
    is_unlocked = serializers.SerializerMethodField()

    class Meta:
        model = ExerciseModule
        fields = ['id', 'title', 'icon', 'course', 'is_unlocked', 'exercises']

    def get_is_unlocked(self, obj):
        user = self.context.get('request').user
        if user and user.is_authenticated:
            if user.is_staff or user.is_superuser:
                return True
            # Vérifie si l'étudiant a terminé le cours associé à ce module d'exercices
            return CourseProgress.objects.filter(
                user=user,              
                course=obj.course, 
                is_completed=True       
            ).exists()
        return False
    
class ExerciseSubmissionSerializer(serializers.ModelSerializer):
    student_id = serializers.IntegerField(source='student.id', read_only=True)
    student_username = serializers.CharField(source='student.first_name', read_only=True)
    exercise_title = serializers.CharField(source='exercise.title', read_only=True)
    exercise_num = serializers.IntegerField(source='exercise.exercise_id', read_only=True)

    class Meta:
        model = ExerciseSubmission
        fields = [
            'id', 
            'student_id', 
            'student_username', 
            'exercise_id', 
            'exercise_title', 
            'exercise_num', 
            'status', 
            'submitted_at'
        ]