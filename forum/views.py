from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import AnswerForm, CommentForm, QuestionForm
from .models import Answer, Comment, Question

def index(request):
    questions = (
        Question.objects.select_related('author')
        .prefetch_related('tags')
        .annotate(answer_count=Count('answers'))
        .order_by('-created_at')
    )

    return render(request, 'forum/index.html', {
        'questions': questions,
        'question_total': Question.objects.count(),
        'answer_total': Answer.objects.count(),
        'member_total': User.objects.count(),
    })

def question_detail(request, pk):
    question = get_object_or_404(
        Question.objects.select_related('author').prefetch_related('tags'),
        pk=pk
    )
    answers = (
        question.answers.select_related('author')
        .prefetch_related(
            Prefetch(
                'comment_set',
                queryset=Comment.objects.select_related('author').order_by('created_at'),
            )
        )
        .order_by('-is_accepted', 'created_at')
    )
    question_comments = (
        question.comment_set.select_related('author').order_by('created_at')
    )
    related_questions = (
        Question.objects.exclude(pk=question.pk)
        .select_related('author')
        .annotate(answer_count=Count('answers'))
        .order_by('-created_at')[:3]
    )
    form = AnswerForm()

    if request.method == 'POST':
        if request.user.is_authenticated:
            form = AnswerForm(request.POST)
            if form.is_valid():
                answer = form.save(commit=False)
                answer.question = question
                answer.author = request.user
                answer.save()
                return redirect('question_detail', pk=question.pk)
        else:
            form = AnswerForm()

    return render(request, 'forum/question_detail.html', {
        'question': question,
        'answers': answers,
        'form': form,
        'question_comments': question_comments,
        'answer_total': answers.count(),
        'related_questions': related_questions,
    })


@login_required
@require_POST
def add_question_comment(request, pk):
    question = get_object_or_404(Question, pk=pk)
    form = CommentForm(
        request.POST,
        instance=Comment(author=request.user, question=question),
    )

    if form.is_valid():
        comment = form.save()
        return redirect(
            f"{reverse('question_detail', kwargs={'pk': question.pk})}"
            f"#comment-{comment.pk}"
        )

    messages.error(request, 'Comment cannot be empty.')
    return redirect('question_detail', pk=question.pk)


@login_required
@require_POST
def add_answer_comment(request, pk):
    answer = get_object_or_404(Answer.objects.select_related('question'), pk=pk)
    form = CommentForm(
        request.POST,
        instance=Comment(author=request.user, answer=answer),
    )

    if form.is_valid():
        comment = form.save()
        return redirect(
            f"{reverse('question_detail', kwargs={'pk': answer.question_id})}"
            f"#comment-{comment.pk}"
        )

    messages.error(request, 'Comment cannot be empty.')
    return redirect('question_detail', pk=answer.question_id)

@login_required
def create_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.save()
            form.save_m2m()
            return redirect('question_detail', pk=question.pk)
    else:
        form = QuestionForm()
    return render(request, 'forum/create_question.html', {'form': form})
