from rest_framework import serializers
from ..models.cours import Course
from ..models.course_payment import CoursePayment
from ..serializers.cours_content import CourseContentSerializer


class CourseSerializer(serializers.ModelSerializer):
    is_free = serializers.SerializerMethodField()
    contents = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "partner",
            "title",
            "description",
            "price",
            "is_free",
            "is_active",
            "contents",
            "created_at",
        ]

    def get_is_free(self, obj):
        return obj.price == 0

    def get_contents(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        # ✅ Cours gratuit
        if obj.price == 0:
            return CourseContentSerializer(
                obj.contents.all(),
                many=True,
                context=self.context
            ).data

        # 🔐 Cours payant
        if user and user.is_authenticated:
            has_paid = CoursePayment.objects.filter(
                user=user,
                course=obj,
                status="paid"
            ).exists()

            if has_paid:
                return CourseContentSerializer(
                    obj.contents.all(),
                    many=True,
                    context=self.context
                ).data

        return []  # 🔒 Contenu bloqué
