import pytest
from django.utils import timezone

from polls.models import Question, Choice


@pytest.fixture()
def question_generator(db):
    def _question_generator(question_text, pub_date=None):
        pub_date = pub_date if pub_date else timezone.now()
        return Question.objects.create(question_text=question_text, pub_date=pub_date)
    return _question_generator


@pytest.fixture()
def question_choice_generator(db):
    def _question_choice_generator(question, choice_text, votes=0):
        return Choice.objects.create(question=question, choice_text=choice_text, votes=votes)
    return _question_choice_generator


@pytest.fixture()
def question(question_generator):
    return question_generator("Question")
