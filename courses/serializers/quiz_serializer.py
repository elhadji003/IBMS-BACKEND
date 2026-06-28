
from rest_framework import serializers
from ..models import Question, Choice


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "text"]


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "text", "choices"]


class QuizSubmissionSerializer(serializers.Serializer):
    answers = serializers.DictField(
        child=serializers.IntegerField(),
        required=True
    )

    def validate_answers(self, value):
        if not value:
            raise serializers.ValidationError(
                "Les réponses sont obligatoires."
            )

        return value
