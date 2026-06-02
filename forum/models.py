from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Question(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return self.title

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    body = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"Answer to {self.question.title} by {self.author}"

class Comment(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(question__isnull=False, answer__isnull=True)
                    | models.Q(question__isnull=True, answer__isnull=False)
                ),
                name='comment_has_exactly_one_target',
            ),
        ]

    def clean(self):
        if (self.question_id is None) == (self.answer_id is None):
            raise ValidationError(
                'A comment must belong to exactly one question or answer.'
            )

    def __str__(self):
        return f'Comment by {self.author}'


class Vote(models.Model):
    UPVOTE = 1
    DOWNVOTE = -1
    VALUE_CHOICES = [
        (UPVOTE, 'Upvote'),
        (DOWNVOTE, 'Downvote'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=VALUE_CHOICES)

    class Meta:
        abstract = True


class QuestionVote(Vote):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='votes',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'question'],
                name='unique_question_vote_per_user',
            ),
            models.CheckConstraint(
                condition=models.Q(value__in=[Vote.DOWNVOTE, Vote.UPVOTE]),
                name='question_vote_value_is_valid',
            ),
        ]


class AnswerVote(Vote):
    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name='votes',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'answer'],
                name='unique_answer_vote_per_user',
            ),
            models.CheckConstraint(
                condition=models.Q(value__in=[Vote.DOWNVOTE, Vote.UPVOTE]),
                name='answer_vote_value_is_valid',
            ),
        ]


class CommentVote(Vote):
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='votes',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'comment'],
                name='unique_comment_vote_per_user',
            ),
            models.CheckConstraint(
                condition=models.Q(value__in=[Vote.DOWNVOTE, Vote.UPVOTE]),
                name='comment_vote_value_is_valid',
            ),
        ]
