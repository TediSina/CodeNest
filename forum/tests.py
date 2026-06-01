from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Question, Tag


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
