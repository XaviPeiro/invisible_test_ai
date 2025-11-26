"""
URL configuration for user-related endpoints.
"""
from django.urls import path

from .views import SignUpView, LoginView, LogoutView, ProfileView, PasswordChangeView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/change-password/', PasswordChangeView.as_view(), name='change-password'),
]

