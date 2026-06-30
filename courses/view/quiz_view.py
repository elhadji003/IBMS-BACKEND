from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from ..models import (
    Course,
    Question,
    QuizSubmission,
    CourseProgress
)

from ..serializers.quiz_serializer import (
    QuestionSerializer,
    QuizSubmissionSerializer
)


class CourseQuizView(APIView):
    permission_classes = [IsAuthenticated]

    # ========================================
    # GET -> récupérer le quiz via course_id
    # ========================================
    def get(self, request, course_id):  # 🌟 Changé : slug -> course_id

        course = get_object_or_404(
            Course,
            id=course_id  # 🌟 Changé : slug=slug -> id=course_id
        )

        questions = Question.objects.filter(
            course=course
        ).prefetch_related("choices")

        if not questions.exists():
            return Response(
                {
                    "detail": "Aucune question disponible."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = QuestionSerializer(
            questions,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    # ========================================
    # POST -> soumettre le quiz via course_id
    # ========================================
    def post(self, request, course_id):  # 🌟 Changé : slug -> course_id

        course = get_object_or_404(
            Course,
            id=course_id  # 🌟 Changé : slug=slug -> id=course_id
        )
        
        serializer = QuizSubmissionSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        user_answers = serializer.validated_data["answers"]

        questions = Question.objects.filter(
            course=course
        ).prefetch_related("choices")

        if not questions.exists():
            return Response(
                {
                    "detail": "Aucun quiz disponible."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        total_questions = questions.count()
        correct_answers_count = 0
        

        for question in questions:

            selected_choice_id = user_answers.get(
                str(question.id)
            )

            if not selected_choice_id:
                continue

            correct_choice = next(
                (
                    choice
                    for choice in question.choices.all()
                    if choice.is_correct
                ),
                None
            )

            if (
                correct_choice
                and correct_choice.id == selected_choice_id
            ):
                correct_answers_count += 1

        score_percentage = round(
            (correct_answers_count / total_questions) * 100
        )

        passed = score_percentage >= 70

        # Sauvegarde tentative
        QuizSubmission.objects.create(
            user=request.user,
            course=course,
            score=score_percentage,
            passed=passed,
        )


        # Mise à jour progression
        xp_gagnes = 0
        if passed:
            progress, _ = CourseProgress.objects.get_or_create(
                user=request.user,
                course=course
            )
                        
            if not progress.is_completed:
                xp_gagnes = 150
                request.user.total_xp += xp_gagnes
                request.user.save(update_fields=['total_xp'])

            progress.progress_percentage = 100
            progress.is_completed = True
            progress.save()

        return Response(
            {
                "score": score_percentage,
                "passed": passed,
                "correct_answers": correct_answers_count,
                "total_questions": total_questions,
                "xp_gagnes": xp_gagnes,
                "total_xp": request.user.total_xp,
                "message": (
                    "Félicitations 🎉 cours validé."
                    if passed
                    else "Score insuffisant, réessayez."
                )
            },
            status=status.HTTP_200_OK
        )