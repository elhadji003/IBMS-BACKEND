from rest_framework import serializers
from courses.models import Course, CourseProgress
from .models import Exercise, ExerciseSubmission

class ExerciseSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    category = serializers.CharField(source="course.category", read_only=True)
    is_unlocked = serializers.SerializerMethodField()

    class Meta:
        model = Exercise
        fields = [
            'id', 'course', 'category', 'exercise_id', 
            'title', 'desc', 'difficulty', 'status', 'is_unlocked' # 2. N'oublie pas de l'exposer
        ]

    def get_status(self, obj):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            submission = ExerciseSubmission.objects.filter(
                student=request.user, 
                exercise=obj
            ).first()
            if submission:
                return submission.status
        return 'not_started'

    # 3. LA LOGIQUE DE DÉBLOCAGE PAR COURS
    def get_is_unlocked(self, obj):
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            return False
            
        user = request.user
        # Les admins/staff ont toujours accès à tout pour tester
        if user.is_staff or user.is_superuser:
            return True

        # On cherche si l'étudiant a fini le cours théorique lié à cet exercice
        try:
            progress = CourseProgress.objects.get(user=user, course=obj.course)
            return progress.is_completed # Renvoie True si le cours est terminé, sinon False
        except CourseProgress.DoesNotExist:
            # Si aucune ligne de progression n'existe, c'est que le cours n'a pas été terminé
            return False

class CourseWithExercisesSerializer(serializers.ModelSerializer):
    """
    Remplace l'ancien ExerciseModuleSerializer.
    Sérialise le cours avec ses exercices directs et calcule si l'accès est déverrouillé.
    """
    exercises = ExerciseSerializer(many=True, read_only=True)
    is_unlocked = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'icon', 'is_unlocked', 'exercises']

    def get_is_unlocked(self, obj):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            user = request.user
            if user.is_staff or user.is_superuser:
                return True
            # Vérifie si l'étudiant a terminé ce cours (obj est directement le Course ici)
            return CourseProgress.objects.filter(
                user=user,              
                course=obj, 
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