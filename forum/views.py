from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Exists, IntegerField, OuterRef, Prefetch, Subquery, Sum, Value
from django.db.models.functions import Coalesce
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods, require_POST

from .forms import AnswerForm, CommentForm, QuestionForm
from .models import Answer, AnswerVote, Comment, CommentVote, Question, QuestionVote, Vote


def _with_vote_data(queryset, vote_model, target_field, user):
    target_lookup = {target_field: OuterRef('pk')}
    vote_totals = (
        vote_model.objects.filter(**target_lookup)
        .values(target_field)
        .annotate(total=Sum('value'))
        .values('total')
    )
    annotations = {
        'vote_score': Coalesce(
            Subquery(vote_totals, output_field=IntegerField()),
            Value(0),
        ),
    }

    if user.is_authenticated:
        annotations.update({
            'is_upvoted': Exists(
                vote_model.objects.filter(
                    user=user,
                    value=Vote.UPVOTE,
                    **target_lookup,
                )
            ),
            'is_downvoted': Exists(
                vote_model.objects.filter(
                    user=user,
                    value=Vote.DOWNVOTE,
                    **target_lookup,
                )
            ),
        })
    else:
        annotations.update({
            'is_upvoted': Value(False),
            'is_downvoted': Value(False),
        })

    return queryset.annotate(**annotations)


def _save_vote(request, item, vote_model, target_field, redirect_url):
    try:
        value = int(request.POST.get('value', ''))
    except ValueError:
        return HttpResponseBadRequest(_('Vote must be an upvote or downvote.'))

    if value not in {Vote.UPVOTE, Vote.DOWNVOTE}:
        return HttpResponseBadRequest(_('Vote must be an upvote or downvote.'))

    lookup = {
        'user': request.user,
        target_field: item,
    }
    existing_vote = vote_model.objects.filter(**lookup).first()

    if existing_vote is None:
        vote_model.objects.create(value=value, **lookup)
        user_vote = value
    elif existing_vote.value == value:
        existing_vote.delete()
        user_vote = 0
    else:
        existing_vote.value = value
        existing_vote.save(update_fields=['value'])
        user_vote = value

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        score = (
            vote_model.objects.filter(**{target_field: item})
            .aggregate(score=Coalesce(Sum('value'), Value(0)))['score']
        )
        return JsonResponse({
            'score': score,
            'user_vote': user_vote,
        })

    return redirect(redirect_url)

def index(request):
    questions = (
        _with_vote_data(
            Question.objects.select_related('author')
            .prefetch_related('tags')
            .annotate(answer_count=Count('answers', distinct=True)),
            QuestionVote,
            'question',
            request.user,
        )
        .order_by('-vote_score', '-created_at')
    )

    return render(request, 'forum/index.html', {
        'questions': questions,
        'question_total': Question.objects.count(),
        'answer_total': Answer.objects.count(),
        'member_total': User.objects.count(),
    })

def question_detail(request, pk):
    question = get_object_or_404(
        _with_vote_data(
            Question.objects.select_related('author').prefetch_related('tags'),
            QuestionVote,
            'question',
            request.user,
        ),
        pk=pk
    )
    answers = (
        _with_vote_data(
            question.answers.select_related('author'),
            AnswerVote,
            'answer',
            request.user,
        )
        .prefetch_related(
            Prefetch(
                'comment_set',
                queryset=_with_vote_data(
                    Comment.objects.select_related('author'),
                    CommentVote,
                    'comment',
                    request.user,
                ).order_by('-vote_score', 'created_at'),
            )
        )
        .order_by('-vote_score', '-is_accepted', 'created_at')
    )
    question_comments = (
        _with_vote_data(
            question.comment_set.select_related('author'),
            CommentVote,
            'comment',
            request.user,
        )
        .order_by('-vote_score', 'created_at')
    )
    related_questions = (
        _with_vote_data(
            Question.objects.exclude(pk=question.pk)
            .select_related('author')
            .annotate(answer_count=Count('answers', distinct=True)),
            QuestionVote,
            'question',
            request.user,
        )
        .order_by('-vote_score', '-created_at')[:3]
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
def vote_question(request, pk):
    question = get_object_or_404(Question, pk=pk)
    return _save_vote(
        request,
        question,
        QuestionVote,
        'question',
        reverse('question_detail', kwargs={'pk': question.pk}),
    )


@login_required
@require_POST
def vote_answer(request, pk):
    answer = get_object_or_404(Answer, pk=pk)
    return _save_vote(
        request,
        answer,
        AnswerVote,
        'answer',
        reverse('question_detail', kwargs={'pk': answer.question_id}),
    )


@login_required
@require_POST
def vote_comment(request, pk):
    comment = get_object_or_404(
        Comment.objects.select_related('answer'),
        pk=pk,
    )
    question_pk = (
        comment.question_id
        if comment.question_id is not None
        else comment.answer.question_id
    )
    return _save_vote(
        request,
        comment,
        CommentVote,
        'comment',
        reverse('question_detail', kwargs={'pk': question_pk}),
    )


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

    messages.error(request, _('Comment cannot be empty.'))
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

    messages.error(request, _('Comment cannot be empty.'))
    return redirect('question_detail', pk=answer.question_id)


@login_required
def edit_question(request, pk):
    question = get_object_or_404(Question, pk=pk, author=request.user)

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect('question_detail', pk=question.pk)
    else:
        form = QuestionForm(instance=question)

    return render(request, 'forum/create_question.html', {
        'form': form,
        'is_edit': True,
        'question': question,
    })


@login_required
def edit_answer(request, pk):
    answer = get_object_or_404(
        Answer.objects.select_related('question'),
        pk=pk,
        author=request.user,
    )

    if request.method == 'POST':
        form = AnswerForm(request.POST, instance=answer)
        if form.is_valid():
            form.save()
            return redirect(
                f"{reverse('question_detail', kwargs={'pk': answer.question_id})}"
                f"#answer-{answer.pk}"
            )
    else:
        form = AnswerForm(instance=answer)

    return render(request, 'forum/edit_answer.html', {
        'answer': answer,
        'form': form,
    })


@login_required
def edit_comment(request, pk):
    comment = get_object_or_404(
        Comment.objects.select_related('question', 'answer__question'),
        pk=pk,
        author=request.user,
    )
    question_pk = (
        comment.question_id
        if comment.question_id is not None
        else comment.answer.question_id
    )

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect(
                f"{reverse('question_detail', kwargs={'pk': question_pk})}"
                f"#comment-{comment.pk}"
            )
    else:
        form = CommentForm(instance=comment)

    return render(request, 'forum/edit_comment.html', {
        'comment': comment,
        'form': form,
        'question_pk': question_pk,
    })


@login_required
@require_http_methods(['GET', 'POST'])
def delete_question(request, pk):
    question = get_object_or_404(Question, pk=pk, author=request.user)

    if request.method == 'POST':
        question.delete()
        messages.success(request, _('Question deleted.'))
        return redirect('index')

    return render(request, 'forum/confirm_delete.html', {
        'title': _('Delete question'),
        'description': _(
            'This permanently deletes the question, its answers, and its comments.'
        ),
        'subject': question.title,
        'cancel_url': reverse('question_detail', kwargs={'pk': question.pk}),
    })


@login_required
@require_http_methods(['GET', 'POST'])
def delete_answer(request, pk):
    answer = get_object_or_404(
        Answer.objects.select_related('question'),
        pk=pk,
        author=request.user,
    )
    question_pk = answer.question_id

    if request.method == 'POST':
        answer.delete()
        messages.success(request, _('Answer deleted.'))
        return redirect('question_detail', pk=question_pk)

    return render(request, 'forum/confirm_delete.html', {
        'title': _('Delete answer'),
        'description': _(
            'This permanently deletes the answer and its comments.'
        ),
        'subject': answer.body,
        'cancel_url': (
            f"{reverse('question_detail', kwargs={'pk': question_pk})}"
            f"#answer-{answer.pk}"
        ),
    })


@login_required
@require_http_methods(['GET', 'POST'])
def delete_comment(request, pk):
    comment = get_object_or_404(
        Comment.objects.select_related('question', 'answer__question'),
        pk=pk,
        author=request.user,
    )
    question_pk = (
        comment.question_id
        if comment.question_id is not None
        else comment.answer.question_id
    )
    return_fragment = (
        f"question-{comment.question_id}"
        if comment.question_id is not None
        else f"answer-{comment.answer_id}"
    )

    if request.method == 'POST':
        comment.delete()
        messages.success(request, _('Comment deleted.'))
        return redirect(
            f"{reverse('question_detail', kwargs={'pk': question_pk})}"
            f"#{return_fragment}"
        )

    return render(request, 'forum/confirm_delete.html', {
        'title': _('Delete comment'),
        'description': _('This permanently deletes the comment.'),
        'subject': comment.content,
        'cancel_url': (
            f"{reverse('question_detail', kwargs={'pk': question_pk})}"
            f"#comment-{comment.pk}"
        ),
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
