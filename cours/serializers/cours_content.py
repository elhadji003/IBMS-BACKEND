from rest_framework import serializers
from ..models.cours_content import CourseContent


class CourseContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseContent
        fields = [
            "id",
            "course",
            "title",
            "file",
            "video_url",
            "order",
        ]
