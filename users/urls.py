from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .view.auth_register import RegisterUserView, LoginUserView, LogoutView
from .views import GetProfileUserView, GetProfileUserByIdView, UpdateProfileUserView, DeleteAccountWithPwd
from .view.view_change_pwd import PasswordChangeView
from .view.view_password import RequestPasswordResetView, PasswordResetConfirmView

urlpatterns = [
    path('token/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    path('register/', RegisterUserView.as_view(), name="register_user"),
    path('login/', LoginUserView.as_view(), name="login_user"),
    path('logout/', LogoutView.as_view(), name="logout_user"),

    # Api pour les users
    path('profile/', GetProfileUserView.as_view(), name="profile_user"),
    path('profile/<int:user_id>/', GetProfileUserByIdView.as_view(), name="profile_user_by_id"),
    path('update/profile/', UpdateProfileUserView.as_view(), name="update_profile_user"),
    path('delete/account/', DeleteAccountWithPwd.as_view(), name="delete_account_user"),

    # Password Management
    path('change-password/user/', PasswordChangeView.as_view(), name="change_password"),
    path('password/request-reset/', RequestPasswordResetView.as_view(), name="request_password_reset"),
    path('password/reset-confirm/<str:uidb64>/<str:token>/', PasswordResetConfirmView.as_view(), name="password_reset_confirm"),

]
