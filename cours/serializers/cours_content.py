from rest_framework import serializers
from ..models.cours_content import CourseContent
from ..models.course_payment import CoursePayment # Importe ton modèle de paiement

class CourseContentSerializer(serializers.ModelSerializer):
    content_type = serializers.SerializerMethodField()
    is_purchased = serializers.SerializerMethodField()

    class Meta:
        model = CourseContent
        fields = [
            "id", "course", "title", "file", 
            "video_url", "video_file", "order", 
            "content_type", "is_purchased"
        ]

    def get_is_purchased(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # CORRECTION : On vérifie le cours parent (obj.course) et non le contenu (obj)
            return CoursePayment.objects.filter(
                user=request.user, 
                course=obj.course,  # <--- Note le .course ici
                status="paid"
            ).exists()
        return False

    def get_content_type(self, obj):
        if obj.video_url: return "video_youtube"
        if hasattr(obj, 'video_file') and obj.video_file: return "video_native"
        if obj.file: return "document"
        return "unknown"

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        
        # SÉCURITÉ : Si le cours est payant et non acheté, on cache les liens
        is_purchased = self.get_is_purchased(instance)
        is_free = instance.course.price == 0 # Vérifie si le cours parent est gratuit

        if not (is_purchased or is_free):
            repr['video_url'] = None
            repr['video_file'] = None
            repr['file'] = None
            repr['locked'] = True # On peut ajouter un flag pour le front
        
        # Nettoyage des champs null
        return {k: v for k, v in repr.items() if v is not None}