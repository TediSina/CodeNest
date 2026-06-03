from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from forum.models import (
    Answer,
    AnswerVote,
    Comment,
    CommentVote,
    Question,
    QuestionVote,
    Tag,
    Vote,
)


DEMO_PASSWORD = "DemoPass123!"

DEMO_USERS = [
    {
        "username": "mentor_mira",
        "email": "mira@example.com",
        "first_name": "Mira",
        "last_name": "Kodra",
    },
    {
        "username": "debug_dion",
        "email": "dion@example.com",
        "first_name": "Dion",
        "last_name": "Hoxha",
    },
    {
        "username": "frontend_era",
        "email": "era@example.com",
        "first_name": "Era",
        "last_name": "Deda",
    },
    {
        "username": "query_ardi",
        "email": "ardi@example.com",
        "first_name": "Ardi",
        "last_name": "Basha",
    },
    {
        "username": "sqlite_ina",
        "email": "ina@example.com",
        "first_name": "Ina",
        "last_name": "Leka",
    },
]

DEMO_TAGS = [
    "django",
    "python",
    "javascript",
    "markdown",
    "sqlite",
    "forms",
    "frontend",
    "querysets",
    "deployment",
]

DEMO_QUESTIONS = [
    {
        "key": "markdown-preview",
        "author": "frontend_era",
        "age_days": 8,
        "title": "Why does my Django template show Markdown instead of formatted code?",
        "tags": ["django", "markdown", "frontend"],
        "body": (
            "I am saving question text as Markdown and rendering it in a Django "
            "template, but code fences show up as plain text.\n\n"
            "The saved body looks like this:\n\n"
            "```python\n"
            "def greet(name):\n"
            "    return f\"Hello, {name}!\"\n"
            "```\n\n"
            "The template prints `{{ question.body }}` inside a div. What is the "
            "right way to turn it into formatted HTML on the page without making "
            "the site unsafe?"
        ),
        "comments": [
            {
                "author": "mentor_mira",
                "age_days": 8,
                "content": (
                    "Are you converting the Markdown in Python or letting the "
                    "browser do it with JavaScript?"
                ),
            },
            {
                "author": "debug_dion",
                "age_days": 7,
                "content": (
                    "If the content comes from users, keep the escaping story clear "
                    "before marking anything safe."
                ),
            },
        ],
        "votes": [
            ("mentor_mira", Vote.UPVOTE),
            ("debug_dion", Vote.UPVOTE),
            ("query_ardi", Vote.UPVOTE),
            ("sqlite_ina", Vote.UPVOTE),
        ],
        "answers": [
            {
                "author": "mentor_mira",
                "age_days": 7,
                "accepted": True,
                "body": (
                    "Use a Markdown renderer, then sanitize or strictly control the "
                    "HTML that gets inserted into the page.\n\n"
                    "For this project, the existing client-side flow can work well:\n\n"
                    "```html\n"
                    "<div class=\"rich-markdown js-markdown\">{{ question.body }}</div>\n"
                    "```\n\n"
                    "Then let the JavaScript convert only those `.js-markdown` nodes. "
                    "That keeps the template simple and makes preview rendering match "
                    "the final post. If you ever switch to server-side Markdown, use a "
                    "sanitizer before applying `safe`."
                ),
                "comments": [
                    {
                        "author": "frontend_era",
                        "age_days": 7,
                        "content": "This matches the preview code I already had. Thanks.",
                    },
                    {
                        "author": "query_ardi",
                        "age_days": 6,
                        "content": "The sanitizer warning is the key part here.",
                    },
                ],
                "votes": [
                    ("frontend_era", Vote.UPVOTE),
                    ("debug_dion", Vote.UPVOTE),
                    ("query_ardi", Vote.UPVOTE),
                    ("sqlite_ina", Vote.UPVOTE),
                ],
            },
            {
                "author": "debug_dion",
                "age_days": 7,
                "accepted": False,
                "body": (
                    "Also check that Showdown and highlight.js are loaded only on "
                    "pages that need them. If the converter script runs before the "
                    "library is loaded, the raw Markdown will remain visible."
                ),
                "comments": [
                    {
                        "author": "frontend_era",
                        "age_days": 7,
                        "content": "Good catch. I had the script order reversed once.",
                    },
                ],
                "votes": [
                    ("mentor_mira", Vote.UPVOTE),
                    ("frontend_era", Vote.UPVOTE),
                ],
            },
        ],
    },
    {
        "key": "duplicate-submit",
        "author": "debug_dion",
        "age_days": 6,
        "title": "How can I stop duplicate form submissions from creating repeated questions?",
        "tags": ["django", "forms"],
        "body": (
            "When I double-click the submit button on the question form, sometimes "
            "two nearly identical questions get created. I already redirect after a "
            "successful POST.\n\n"
            "Should I solve this in the database, in the view, or with JavaScript?"
        ),
        "comments": [
            {
                "author": "mentor_mira",
                "age_days": 6,
                "content": "Redirect-after-POST helps refreshes, but it does not stop every double submit.",
            },
        ],
        "votes": [
            ("mentor_mira", Vote.UPVOTE),
            ("frontend_era", Vote.UPVOTE),
            ("query_ardi", Vote.UPVOTE),
        ],
        "answers": [
            {
                "author": "query_ardi",
                "age_days": 5,
                "accepted": True,
                "body": (
                    "Use layers, because each one protects a different failure mode.\n\n"
                    "1. Keep redirect-after-POST in the view.\n"
                    "2. Disable the submit button after the first click for a nicer UX.\n"
                    "3. Add a server-side rule if duplicates are truly invalid.\n\n"
                    "For example, you could detect recent questions by the same author "
                    "with the same normalized title before saving. I would not add a "
                    "global unique constraint on title, because two people can ask the "
                    "same thing in different contexts."
                ),
                "comments": [
                    {
                        "author": "debug_dion",
                        "age_days": 5,
                        "content": "The normalized-title check sounds like the right fit.",
                    },
                    {
                        "author": "mentor_mira",
                        "age_days": 5,
                        "content": "Agreed. A database constraint would be too blunt here.",
                    },
                ],
                "votes": [
                    ("debug_dion", Vote.UPVOTE),
                    ("mentor_mira", Vote.UPVOTE),
                    ("frontend_era", Vote.UPVOTE),
                ],
            },
            {
                "author": "frontend_era",
                "age_days": 5,
                "accepted": False,
                "body": (
                    "On the browser side, add a small submit handler that sets "
                    "`button.disabled = true` after the form validates. It will not "
                    "replace server-side checks, but it makes the UI feel much more "
                    "intentional."
                ),
                "comments": [
                    {
                        "author": "sqlite_ina",
                        "age_days": 4,
                        "content": "This is especially useful during slow local demos.",
                    },
                ],
                "votes": [
                    ("debug_dion", Vote.UPVOTE),
                    ("mentor_mira", Vote.UPVOTE),
                ],
            },
        ],
    },
    {
        "key": "split-js",
        "author": "mentor_mira",
        "age_days": 4,
        "title": "Best way to split a large JavaScript file for a small forum app?",
        "tags": ["javascript", "frontend"],
        "body": (
            "Our forum has Markdown preview, vote buttons, and small form helpers. "
            "Right now everything is drifting into one big JavaScript file.\n\n"
            "I do not want a full build system yet. What is a practical structure "
            "for plain static files in Django?"
        ),
        "comments": [
            {
                "author": "frontend_era",
                "age_days": 4,
                "content": "Are these scripts needed on every page or only on detail/create pages?",
            },
        ],
        "votes": [
            ("frontend_era", Vote.UPVOTE),
            ("debug_dion", Vote.UPVOTE),
        ],
        "answers": [
            {
                "author": "frontend_era",
                "age_days": 4,
                "accepted": True,
                "body": (
                    "Split by page behavior first, not by tiny utilities.\n\n"
                    "A simple setup could be:\n\n"
                    "```text\n"
                    "static/js/markdown_editor.js\n"
                    "static/js/question_detail.js\n"
                    "static/js/create_question.js\n"
                    "```\n\n"
                    "Load each file only in the template block for the page that uses "
                    "it. This keeps the code understandable without introducing npm, "
                    "bundling, or module loading too early."
                ),
                "comments": [
                    {
                        "author": "mentor_mira",
                        "age_days": 4,
                        "content": "That gives us enough structure without changing the stack.",
                    },
                ],
                "votes": [
                    ("mentor_mira", Vote.UPVOTE),
                    ("debug_dion", Vote.UPVOTE),
                    ("query_ardi", Vote.UPVOTE),
                ],
            },
            {
                "author": "debug_dion",
                "age_days": 3,
                "accepted": False,
                "body": (
                    "One extra rule: make each file resilient if the expected DOM node "
                    "is missing. A short guard like `if (!form) return;` prevents "
                    "template changes from breaking unrelated pages."
                ),
                "comments": [
                    {
                        "author": "frontend_era",
                        "age_days": 3,
                        "content": "Small guard clauses save a surprising amount of demo stress.",
                    },
                ],
                "votes": [
                    ("mentor_mira", Vote.UPVOTE),
                    ("frontend_era", Vote.UPVOTE),
                ],
            },
        ],
    },
    {
        "key": "multi-tag-filter",
        "author": "query_ardi",
        "age_days": 3,
        "title": "How do I filter questions by multiple tags in Django?",
        "tags": ["django", "querysets"],
        "body": (
            "I can show all questions for one tag with `tag.question_set.all()`. "
            "Now I want to support URLs like `?tags=django,forms` and return "
            "questions that contain every selected tag.\n\n"
            "What query should I use?"
        ),
        "comments": [
            {
                "author": "sqlite_ina",
                "age_days": 3,
                "content": "Do you want any selected tag or all selected tags?",
            },
            {
                "author": "query_ardi",
                "age_days": 3,
                "content": "All selected tags. The result should narrow down as tags are added.",
            },
        ],
        "votes": [
            ("mentor_mira", Vote.UPVOTE),
            ("debug_dion", Vote.UPVOTE),
            ("frontend_era", Vote.UPVOTE),
            ("sqlite_ina", Vote.UPVOTE),
        ],
        "answers": [
            {
                "author": "sqlite_ina",
                "age_days": 2,
                "accepted": True,
                "body": (
                    "Filter once per selected tag. Chaining filters over a many-to-many "
                    "relationship gives you the intersection:\n\n"
                    "```python\n"
                    "questions = Question.objects.all()\n"
                    "for tag_name in selected_tags:\n"
                    "    questions = questions.filter(tags__name=tag_name)\n"
                    "questions = questions.distinct()\n"
                    "```\n\n"
                    "If you need counts or ranking afterward, add your annotations after "
                    "the filters so they run on the narrowed queryset."
                ),
                "comments": [
                    {
                        "author": "query_ardi",
                        "age_days": 2,
                        "content": "That is exactly the intersection behavior I needed.",
                    },
                    {
                        "author": "mentor_mira",
                        "age_days": 2,
                        "content": "Nice compact solution. It also reads well in a view.",
                    },
                ],
                "votes": [
                    ("query_ardi", Vote.UPVOTE),
                    ("mentor_mira", Vote.UPVOTE),
                    ("debug_dion", Vote.UPVOTE),
                    ("frontend_era", Vote.UPVOTE),
                ],
            },
            {
                "author": "mentor_mira",
                "age_days": 2,
                "accepted": False,
                "body": (
                    "If performance becomes a concern later, profile the generated SQL "
                    "before changing the code. For a small forum, the chained filter "
                    "approach is usually clear and fast enough."
                ),
                "comments": [
                    {
                        "author": "query_ardi",
                        "age_days": 2,
                        "content": "Keeping it simple for now sounds good.",
                    },
                ],
                "votes": [
                    ("query_ardi", Vote.UPVOTE),
                    ("sqlite_ina", Vote.UPVOTE),
                ],
            },
        ],
    },
    {
        "key": "sqlite-demo-data",
        "author": "sqlite_ina",
        "age_days": 1,
        "title": "SQLite database works locally but teammates see no questions",
        "tags": ["sqlite", "django", "deployment"],
        "body": (
            "I pushed the project and everyone can run the Django server, but their "
            "home page has no questions. My local `db.sqlite3` has data.\n\n"
            "Should we commit the SQLite file, create fixtures, or write a script?"
        ),
        "comments": [
            {
                "author": "debug_dion",
                "age_days": 1,
                "content": "For a class demo, a seed command is usually easier than asking everyone to share one DB file.",
            },
        ],
        "votes": [
            ("mentor_mira", Vote.UPVOTE),
            ("debug_dion", Vote.UPVOTE),
            ("frontend_era", Vote.UPVOTE),
            ("query_ardi", Vote.UPVOTE),
        ],
        "answers": [
            {
                "author": "debug_dion",
                "age_days": 1,
                "accepted": True,
                "body": (
                    "Write a seed script or management command. It keeps the demo data "
                    "documented and repeatable:\n\n"
                    "```bash\n"
                    "python manage.py migrate\n"
                    "python manage.py seed_demo_data\n"
                    "```\n\n"
                    "Committing SQLite can be fine for a tiny school project, but it is "
                    "easy for the file to drift. A command also lets you create users, "
                    "votes, comments, and accepted answers in one place."
                ),
                "comments": [
                    {
                        "author": "sqlite_ina",
                        "age_days": 1,
                        "content": "I like that it explains the demo state in code.",
                    },
                    {
                        "author": "frontend_era",
                        "age_days": 1,
                        "content": "It also makes screenshots and presentations much more reliable.",
                    },
                ],
                "votes": [
                    ("sqlite_ina", Vote.UPVOTE),
                    ("mentor_mira", Vote.UPVOTE),
                    ("frontend_era", Vote.UPVOTE),
                    ("query_ardi", Vote.UPVOTE),
                ],
            },
            {
                "author": "query_ardi",
                "age_days": 1,
                "accepted": False,
                "body": (
                    "Fixtures are another option, especially if you want JSON data that "
                    "Django can load with `loaddata`. I prefer a command here because it "
                    "can hash passwords and create votes with normal model code."
                ),
                "comments": [
                    {
                        "author": "sqlite_ina",
                        "age_days": 1,
                        "content": "Password hashing is a good reason to use the command.",
                    },
                ],
                "votes": [
                    ("sqlite_ina", Vote.UPVOTE),
                    ("debug_dion", Vote.UPVOTE),
                ],
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Create repeatable demo users, questions, answers, comments, tags, and votes."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            default=DEMO_PASSWORD,
            help="Password to set for every seeded demo user.",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete the known demo records before creating them again.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        password = options["password"]

        if options["reset"]:
            self._delete_existing_demo_data()

        users = self._seed_users(password)
        tags = self._seed_tags()
        questions, answers, comments = self._seed_threads(users, tags)

        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
        self.stdout.write(f"Users: {len(users)}")
        self.stdout.write(f"Tags: {len(tags)}")
        self.stdout.write(f"Questions: {len(questions)}")
        self.stdout.write(f"Answers: {len(answers)}")
        self.stdout.write(f"Comments: {len(comments)}")
        self.stdout.write("Demo login usernames:")
        for username in users:
            self.stdout.write(f"  - {username}")
        self.stdout.write(f"Demo password for all seeded users: {password}")

    def _delete_existing_demo_data(self):
        usernames = [user["username"] for user in DEMO_USERS]
        titles = [question["title"] for question in DEMO_QUESTIONS]

        Question.objects.filter(title__in=titles).delete()
        User.objects.filter(username__in=usernames).delete()
        Tag.objects.filter(name__in=DEMO_TAGS, question__isnull=True).delete()

    def _seed_users(self, password):
        users = {}

        for user_data in DEMO_USERS:
            user, _ = User.objects.get_or_create(username=user_data["username"])
            user.email = user_data["email"]
            user.first_name = user_data["first_name"]
            user.last_name = user_data["last_name"]
            user.set_password(password)
            user.save()
            users[user.username] = user

        return users

    def _seed_tags(self):
        tags = {}

        for tag_name in DEMO_TAGS:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            tags[tag_name] = tag

        return tags

    def _seed_threads(self, users, tags):
        now = timezone.now()
        questions = {}
        answers = []
        comments = []

        for question_data in DEMO_QUESTIONS:
            question_created = now - timedelta(days=question_data["age_days"])
            question, _ = Question.objects.update_or_create(
                title=question_data["title"],
                defaults={
                    "author": users[question_data["author"]],
                    "body": question_data["body"],
                },
            )
            question.tags.set(tags[tag_name] for tag_name in question_data["tags"])
            self._set_timestamps(Question, question.pk, question_created)
            questions[question_data["key"]] = question

            comments.extend(
                self._seed_question_comments(question, question_data, users, now)
            )
            self._seed_question_votes(question, question_data, users)

            for answer_data in question_data["answers"]:
                answer_created = now - timedelta(days=answer_data["age_days"])
                answer, _ = Answer.objects.get_or_create(
                    question=question,
                    author=users[answer_data["author"]],
                    body=answer_data["body"],
                    defaults={"is_accepted": answer_data["accepted"]},
                )
                answer.is_accepted = answer_data["accepted"]
                answer.save(update_fields=["is_accepted"])
                self._set_timestamps(Answer, answer.pk, answer_created)
                answers.append(answer)

                comments.extend(
                    self._seed_answer_comments(answer, answer_data, users, now)
                )
                self._seed_answer_votes(answer, answer_data, users)

        self._seed_comment_votes(comments, users)

        return questions, answers, comments

    def _seed_question_comments(self, question, question_data, users, now):
        comments = []

        for comment_data in question_data["comments"]:
            created_at = now - timedelta(days=comment_data["age_days"])
            comment, _ = Comment.objects.get_or_create(
                question=question,
                answer=None,
                author=users[comment_data["author"]],
                content=comment_data["content"],
            )
            self._set_timestamps(Comment, comment.pk, created_at)
            comments.append(comment)

        return comments

    def _seed_answer_comments(self, answer, answer_data, users, now):
        comments = []

        for comment_data in answer_data["comments"]:
            created_at = now - timedelta(days=comment_data["age_days"])
            comment, _ = Comment.objects.get_or_create(
                question=None,
                answer=answer,
                author=users[comment_data["author"]],
                content=comment_data["content"],
            )
            self._set_timestamps(Comment, comment.pk, created_at)
            comments.append(comment)

        return comments

    def _seed_question_votes(self, question, question_data, users):
        for username, value in question_data["votes"]:
            QuestionVote.objects.update_or_create(
                question=question,
                user=users[username],
                defaults={"value": value},
            )

    def _seed_answer_votes(self, answer, answer_data, users):
        for username, value in answer_data["votes"]:
            AnswerVote.objects.update_or_create(
                answer=answer,
                user=users[username],
                defaults={"value": value},
            )

    def _seed_comment_votes(self, comments, users):
        voter_names = list(users.keys())

        for index, comment in enumerate(comments):
            voter = users[voter_names[index % len(voter_names)]]

            if voter == comment.author:
                voter = users[voter_names[(index + 1) % len(voter_names)]]

            CommentVote.objects.update_or_create(
                comment=comment,
                user=voter,
                defaults={"value": Vote.UPVOTE},
            )

    def _set_timestamps(self, model, pk, created_at):
        fields = {"created_at": created_at}

        if any(field.name == "updated_at" for field in model._meta.fields):
            fields["updated_at"] = created_at + timedelta(hours=2)

        model.objects.filter(pk=pk).update(**fields)
