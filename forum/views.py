from django.shortcuts import render, get_object_or_404, redirect
from .models import Question
from django.contrib.auth.decorators import login_required
from .forms import QuestionForm

def index(request):
    questions = Question.objects.all().order_by('-created_at')
    return render(request, 'forum/index.html', {'questions': questions})

def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    answers = question.answers.all()

    return render(request, 'forum/question_detail.html', {
        'question': question,
        'answers': answers
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
