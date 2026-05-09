from django.urls import path
from . import views

urlpatterns = [
    path('analytics/', views.analytics_overview, name='analytics_overview'),
]
