from rest_framework import serializers
from ..models.user import User

class ProfileUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone_number", 
                "email", "role", "avatar", "created_at",]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request", None)

        if instance.avatar and request:
            data["avatar"] = request.build_absolute_uri(instance.avatar.url)

        return data
