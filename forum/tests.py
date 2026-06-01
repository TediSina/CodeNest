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


class ContentEditTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username='content-author',
            password='test-password',
        )
        self.other_user = User.objects.create_user(
            username='other-user',
            password='test-password',
        )
        self.question = Question.objects.create(
            title='Original question title',
            body='Original question body',
            author=self.author,
        )
        self.python_tag = Tag.objects.create(name='python')
        self.question.tags.add(self.python_tag)
        self.answer = Answer.objects.create(
            question=self.question,
            body='Original answer body',
            author=self.author,
        )
        self.question_comment = Comment.objects.create(
            content='Original question comment',
            author=self.author,
            question=self.question,
        )
        self.answer_comment = Comment.objects.create(
            content='Original answer comment',
            author=self.author,
            answer=self.answer,
        )

    def test_question_edit_form_includes_existing_tags(self):
        self.client.force_login(self.author)

        response = self.client.get(
            reverse('edit_question', args=[self.question.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form']['tags'].value(), 'python')

    def test_author_can_open_answer_and_comment_editors(self):
        self.client.force_login(self.author)

        answer_response = self.client.get(
            reverse('edit_answer', args=[self.answer.pk])
        )
        comment_response = self.client.get(
            reverse('edit_comment', args=[self.answer_comment.pk])
        )

        self.assertEqual(answer_response.status_code, 200)
        self.assertContains(answer_response, 'Original answer body')
        self.assertEqual(comment_response.status_code, 200)
        self.assertContains(comment_response, 'Original answer comment')

    def test_author_can_edit_a_question_and_replace_tags(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse('edit_question', args=[self.question.pk]),
            {
                'title': 'Updated question title',
                'body': 'Updated question body',
                'tags': 'django, testing',
            },
        )

        self.question.refresh_from_db()

        self.assertRedirects(
            response,
            reverse('question_detail', args=[self.question.pk]),
        )
        self.assertEqual(self.question.title, 'Updated question title')
        self.assertEqual(self.question.body, 'Updated question body')
        self.assertCountEqual(
            self.question.tags.values_list('name', flat=True),
            ['django', 'testing'],
        )

    def test_author_can_edit_an_answer(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse('edit_answer', args=[self.answer.pk]),
            {'body': 'Updated answer body'},
        )

        self.answer.refresh_from_db()

        self.assertRedirects(
            response,
            f"{reverse('question_detail', args=[self.question.pk])}"
            f"#answer-{self.answer.pk}",
        )
        self.assertEqual(self.answer.body, 'Updated answer body')

    def test_author_can_edit_a_question_comment(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse('edit_comment', args=[self.question_comment.pk]),
            {'content': 'Updated question comment'},
        )

        self.question_comment.refresh_from_db()

        self.assertRedirects(
            response,
            f"{reverse('question_detail', args=[self.question.pk])}"
            f"#comment-{self.question_comment.pk}",
        )
        self.assertEqual(
            self.question_comment.content,
            'Updated question comment',
        )

    def test_author_can_edit_an_answer_comment(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse('edit_comment', args=[self.answer_comment.pk]),
            {'content': 'Updated answer comment'},
        )

        self.answer_comment.refresh_from_db()

        self.assertRedirects(
            response,
            f"{reverse('question_detail', args=[self.question.pk])}"
            f"#comment-{self.answer_comment.pk}",
        )
        self.assertEqual(self.answer_comment.content, 'Updated answer comment')

    def test_user_cannot_edit_another_users_content(self):
        self.client.force_login(self.other_user)
        urls = [
            reverse('edit_question', args=[self.question.pk]),
            reverse('edit_answer', args=[self.answer.pk]),
            reverse('edit_comment', args=[self.question_comment.pk]),
        ]

        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 404)
                self.assertEqual(self.client.post(url, {}).status_code, 404)

    def test_anonymous_user_is_redirected_to_sign_in(self):
        url = reverse('edit_question', args=[self.question.pk])

        response = self.client.get(url)

        self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_thread_only_shows_edit_links_for_the_content_author(self):
        thread_url = reverse('question_detail', args=[self.question.pk])
        edit_urls = [
            reverse('edit_question', args=[self.question.pk]),
            reverse('edit_answer', args=[self.answer.pk]),
            reverse('edit_comment', args=[self.question_comment.pk]),
            reverse('edit_comment', args=[self.answer_comment.pk]),
        ]

        self.client.force_login(self.author)
        author_response = self.client.get(thread_url)

        for url in edit_urls:
            with self.subTest(url=url):
                self.assertContains(author_response, url)

        self.client.force_login(self.other_user)
        other_user_response = self.client.get(thread_url)

        for url in edit_urls:
            with self.subTest(url=url):
                self.assertNotContains(other_user_response, url)
