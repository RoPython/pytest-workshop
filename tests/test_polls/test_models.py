from datetime import timedelta
from django.utils import timezone

from polls.models import Question


def test_question_was_published_recently():
    now = timezone.now()
    question1 = Question(question_text="Question 1", pub_date=now)
    assert question1.was_published_recently() is True

    question2 = Question(question_text="Question 2", pub_date=now - timedelta(days=2))
    assert question2.was_published_recently() is False

    question3 = Question(question_text="Question 3", pub_date=now + timedelta(days=1))
    assert question3.was_published_recently() is False
