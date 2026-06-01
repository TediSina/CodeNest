from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Answer, Comment, Question, Tag


class CreateQuestionTagsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='tag-author',
            password='test-password',
        )
        self.client.force_login(self.user)

    def test_user_can_create_tags_while_posting_a_question(self):
        response = self.client.post(reverse('create_question'), {
            'title': 'How do I test free-form tags?',
            'body': 'I want to add tags that do not exist yet.',
            'tags': 'Python, django, #Testing',
        })

        question = Question.objects.get(title='How do I test free-form tags?')

        self.assertRedirects(
            response,
            reverse('question_detail', args=[question.pk]),
        )
        self.assertCountEqual(
            question.tags.values_list('name', flat=True),
            ['python', 'django', 'testing'],
        )

    def test_existing_tags_are_reused_and_duplicate_names_are_ignored(self):
        python_tag = Tag.objects.create(name='Python')

        self.client.post(reverse('create_question'), {
            'title': 'Will existing tags be reused?',
            'body': 'Tags should not be duplicated by capitalization.',
            'tags': '#python, Python, django',
        })

        question = Question.objects.get(title='Will existing tags be reused?')

        self.assertCountEqual(
            question.tags.values_list('pk', flat=True),
            [python_tag.pk, Tag.objects.get(name='django').pk],
        )
        self.assertEqual(Tag.objects.filter(name__iexact='python').count(), 1)

    def test_tag_names_cannot_exceed_the_database_limit(self):
        response = self.client.post(reverse('create_question'), {
            'title': 'Can a tag be too long?',
            'body': 'The form should explain the limit.',
            'tags': 'x' * 51,
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tags must be 50 characters or fewer.')
        self.assertFalse(Question.objects.exists())


class CommentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='comment-author',
            password='test-password',
        )
        self.question = Question.objects.create(
            title='How should comments work?',
            body='Comments should be attached to one post.',
            author=self.user,
        )
        self.answer = Answer.objects.create(
            question=self.question,
            body='They should stay compact.',
            author=self.user,
        )

    def test_authenticated_user_can_comment_on_a_question(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('add_question_comment', args=[self.question.pk]),
            {'content': 'Could you include a reproducible example?'},
        )

        comment = Comment.objects.get()

        self.assertRedirects(
            response,
            f"{reverse('question_detail', args=[self.question.pk])}"
            f"#comment-{comment.pk}",
        )
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.question, self.question)
        self.assertIsNone(comment.answer)

    def test_authenticated_user_can_comment_on_an_answer(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('add_answer_comment', args=[self.answer.pk]),
            {'content': 'This also works for the earlier version.'},
        )

        comment = Comment.objects.get()

        self.assertRedirects(
            response,
            f"{reverse('question_detail', args=[self.question.pk])}"
            f"#comment-{comment.pk}",
        )
        self.assertEqual(comment.answer, self.answer)
        self.assertIsNone(comment.question)

    def test_thread_displays_question_and_answer_comments(self):
        Comment.objects.create(
            content='Question comment',
            author=self.user,
            question=self.question,
        )
        Comment.objects.create(
            content='Answer comment',
            author=self.user,
            answer=self.answer,
        )

        response = self.client.get(
            reverse('question_detail', args=[self.question.pk])
        )

        self.assertContains(response, 'Question comment')
        self.assertContains(response, 'Answer comment')
        self.assertContains(response, 'Sign in to add a comment', count=2)

    def test_anonymous_user_cannot_add_a_comment(self):
        response = self.client.post(
            reverse('add_question_comment', args=[self.question.pk]),
            {'content': 'Anonymous comment'},
        )

        self.assertRedirects(
            response,
            f"{reverse('login')}?next="
            f"{reverse('add_question_comment', args=[self.question.pk])}",
        )
        self.assertFalse(Comment.objects.exists())

    def test_empty_comment_is_not_saved(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('add_question_comment', args=[self.question.pk]),
            {'content': '   '},
        )

        self.assertRedirects(
            response,
            reverse('question_detail', args=[self.question.pk]),
        )
        self.assertFalse(Comment.objects.exists())

    def test_comment_requires_exactly_one_target(self):
        comment = Comment(content='Missing target', author=self.user)

        with self.assertRaises(ValidationError):
            comment.full_clean()
