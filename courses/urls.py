from django.urls import path
from .view.courses_view import CourseListView, CourseTabListView, CourseDetailView, UpdateCourseProgressView, UserCourseStatsView, CoursCountView
from .view.quiz_view import CourseQuizView

urlpatterns = [
    path('', CourseListView.as_view(), name='course-list'),
    path('tabs/', CourseTabListView.as_view(), name="courses_tabs"),
    path('<int:course_id>/progress/', UpdateCourseProgressView.as_view(), name='course-progress'),
    path('<int:course_id>/', CourseDetailView.as_view(), name='course-detail'),
    path('<int:course_id>/quiz/', CourseQuizView.as_view(), name='course-quiz'),
    path('me/stats/', UserCourseStatsView.as_view(), name='user-course-stats'),
    path('count/courses/', CoursCountView.as_view(), name='courses_count'),
]