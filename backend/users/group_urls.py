"""
URL configuration for group-related endpoints.
"""
from django.urls import path

from .views import GroupListView, GroupDetailView, GroupMembersView

urlpatterns = [
    path('', GroupListView.as_view(), name='group-list'),
    path('<uuid:group_id>/', GroupDetailView.as_view(), name='group-detail'),
    path('<uuid:group_id>/members/', GroupMembersView.as_view(), name='group-members'),
]

