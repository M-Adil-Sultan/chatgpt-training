from django.urls import path
from . import views

urlpatterns = [
    path('', views.train, name='train'),
    path('upload_excel/', views.upload_excel, name='upload_excel'),
    path('delete/<int:id>/', views.delete, name='delete'),
    path('search/', views.search_train_dataset, name='search_train_dataset'),
    path('insert_via_form/', views.insert_via_form, name='insert_via_form'),
]