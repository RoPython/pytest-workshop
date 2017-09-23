from datetime import timedelta
from django.utils import timezone

from polls.models import Question
from polls.views import IndexView

index_view = IndexView.as_view()


def test_index_view_no_question(rf, db):
    request = rf.get('')
    response = index_view(request)
    assert response.status_code == 200
    assert list(response.context_data['latest_question_list']) == []


def test_index_view_one_question(rf, db):
    now = timezone.now()
    question1 = Question.objects.create(question_text="Question 1", pub_date=now)

    request = rf.get('')
    response = index_view(request)
    assert response.status_code == 200
    assert list(response.context_data['latest_question_list']) == [question1]


def test_index_view_two_questions(rf, db):
    now = timezone.now()
    question1 = Question.objects.create(question_text="Question 1", pub_date=now)
    question2 = Question.objects.create(question_text="Question 2", pub_date=now - timedelta(hours=1))

    request = rf.get('')
    response = index_view(request)
    assert response.status_code == 200
    assert list(response.context_data['latest_question_list']) == [question1, question2]


def test_index_view_only_last_five_questions(rf, db):
    now = timezone.now()

    questions = []
    for i in range(0, 10):
        questions.append(Question.objects.create(
            question_text="Question {}".format(i), pub_date=now - timedelta(hours=i)
        ))

    request = rf.get('')
    response = index_view(request)
    assert response.status_code == 200
    assert list(response.context_data['latest_question_list']) == questions[:5]


def test_index_view_exclude_question_published_in_future(rf, db):
    now = timezone.now()
    question1 = Question.objects.create(question_text="Question 1", pub_date=now)
    question2 = Question.objects.create(question_text="Question 2", pub_date=now + timedelta(hours=1))

    request = rf.get('')
    response = index_view(request)
    assert response.status_code == 200
    assert list(response.context_data['latest_question_list']) == [question1]
