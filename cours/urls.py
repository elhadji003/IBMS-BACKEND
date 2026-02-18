from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, CourseContentViewSet

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"courses-content", CourseContentViewSet, basename="course-content")

urlpatterns = router.urls
