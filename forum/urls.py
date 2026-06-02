from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('tags/', views.tag_list, name='tag_list'),
    path('tags/<int:pk>/', views.tag_questions, name='tag_questions'),
    path('question/<int:pk>/', views.question_detail, name='question_detail'),
    path('question/<int:pk>/vote/', views.vote_question, name='vote_question'),
    path('question/<int:pk>/comment/', views.add_question_comment, name='add_question_comment'),
    path('question/<int:pk>/edit/', views.edit_question, name='edit_question'),
    path('question/<int:pk>/delete/', views.delete_question, name='delete_question'),
    path('answer/<int:pk>/vote/', views.vote_answer, name='vote_answer'),
    path('answer/<int:pk>/comment/', views.add_answer_comment, name='add_answer_comment'),
    path('answer/<int:pk>/edit/', views.edit_answer, name='edit_answer'),
    path('answer/<int:pk>/delete/', views.delete_answer, name='delete_answer'),
    path('comment/<int:pk>/vote/', views.vote_comment, name='vote_comment'),
    path('comment/<int:pk>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
    path('create/', views.create_question, name='create_question'),
]
