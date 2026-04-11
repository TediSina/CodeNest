from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .models import Question, Answer
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .forms import QuestionForm, AnswerForm

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
    answers = question.answers.select_related('author').order_by('-is_accepted', 'created_at')
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
        'answer_total': answers.count(),
        'related_questions': related_questions,
    })

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
