from django.urls import path
from .views.buy_course import buy_course
from .views.callback import paydunya_callback

urlpatterns = [
    # 💳 Acheter un cours
    path("courses/<int:course_id>/buy/", buy_course, name="buy_course"),

    # 🔔 Callback Paydunya
    path("paydunya/callback/", paydunya_callback, name="paydunya_callback"),
]