from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExerciseModuleViewSet

router = DefaultRouter()
router.register(r'exercices', ExerciseModuleViewSet, basename='exercice')

urlpatterns = [
    path('', include(router.urls)),
]