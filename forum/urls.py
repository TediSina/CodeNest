from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('question/<int:pk>/', views.question_detail, name='question_detail'),
    path('create/', views.create_question, name='create_question'),
]
