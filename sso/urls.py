from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from django.urls import path
from . import views


app_name = 'sso'
urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token-verify'),
    
    path('register/', views.UserRegisterView.as_view()),
    path('user/<str:username>/', views.UserProfileView.as_view()),
    path('verify/', views.UserVerifyView.as_view()),
    path('change_password/', views.UserChangePasswordView.as_view()),
    path('forgot_password/', views.ForgotPasswordView.as_view()),
    path('reset_password/', views.ResetPasswordView.as_view()),
]
