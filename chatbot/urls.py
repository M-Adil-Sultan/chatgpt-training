from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('chatbot', views.chatbot, name='chatbot'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='logout'),
    path('chatlog', views.chatlog, name='chatlog'),
    path('insert_to_train/<int:chat_id>/', views.insert_to_train, name='insert_to_train'),
    path('modify_log/', views.modify_log, name='modify_log'),
    path('chain_initializer/', views.chain_initializer, name='chain_initializer'),
    path('approve/<int:user_id>/', views.approve_user, name='approve_user'),

]
