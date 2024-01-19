from django.urls import path
from . import views

urlpatterns = [
    path('', views.train, name='train'),
    path('upload_excel/', views.upload_excel, name='upload_excel'),
    path('delete/<int:id>/', views.delete, name='delete'),
    
]