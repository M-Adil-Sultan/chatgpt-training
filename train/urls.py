from django.urls import path
from . import views

urlpatterns = [
    path('', views.train, name='train'),
    path('delete/<int:id>/', views.delete, name='delete'),
    
]