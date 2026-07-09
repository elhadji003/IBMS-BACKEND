from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        # L'étudiant ne voit QUE ses propres notifications
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_as_read(self, request, pk=None):
        """
        Action personnalisée pour passer 'is_read' à True
        Exemple d'URL : /api/notifications/<id>/mark-read/
        """
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"detail": "Notification marquée comme lue."}, status=status.HTTP_200_OK)