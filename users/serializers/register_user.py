from rest_framework import serializers
from ..models.user import User


class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "role", "email", "phone_number", "password"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate(self, data):
        email = data.get("email")
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {"email": "Cet email est déjà utilisé"}
            )
        return data

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
