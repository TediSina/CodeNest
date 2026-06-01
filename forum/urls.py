from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('question/<int:pk>/', views.question_detail, name='question_detail'),
    path('question/<int:pk>/comment/', views.add_question_comment, name='add_question_comment'),
    path('answer/<int:pk>/comment/', views.add_answer_comment, name='add_answer_comment'),
    path('create/', views.create_question, name='create_question'),
]
