from django.urls import path
from .view.courses_view import CourseListView, CourseDetailView, UpdateCourseProgressView, UserCourseStatsView
from .view.quiz_view import CourseQuizView

urlpatterns = [
    path('', CourseListView.as_view(), name='course-list'),
    # On passe du slug à l'id ici :
    path('<int:course_id>/progress/', UpdateCourseProgressView.as_view(), name='course-progress'),
    path('<int:course_id>/', CourseDetailView.as_view(), name='course-detail'),
    path('<int:course_id>/quiz/', CourseQuizView.as_view(), name='course-quiz'),
    path('me/stats/', UserCourseStatsView.as_view(), name='user-course-stats'),
]