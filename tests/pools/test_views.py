from datetime import timedelta

import pytest
from django.http import Http404
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.html import escape

from polls.models import Question, Choice
from polls.views import IndexView, vote, DetailView, ResultsView

index_view = IndexView.as_view()


def test_index_view_no_question(rf, db):
    request = rf.get('/')
    response = index_view(request)
    assert response.status_code == 200
    assert list(response.context_data['latest_question_list']) == []


def test_index_view_one_question(rf, db):
    now = timezone.now()
    question1 = Question.objects.create(question_text="Question 1", pub_date=now)

    request = rf.get('/')
    response = index_view(request)
    assert response.status_code == 200
    assert list(response.context_data['latest_question_list']) == [question1]


def test_index_view_two_questions(rf, db):
    now = timezone.now()
    question1 = Question.objects.create(question_text="Question 1", pub_date=now)
    question2 = Question.objects.create(question_text="Question 2", pub_date=now - timedelta(hours=1))

    request = rf.get('/')
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

    request = rf.get('/')
    response = index_view(request)
    assert response.status_code == 200
    assert list(response.context_data['latest_question_list']) == questions[:5]


def test_index_view_exclude_question_published_in_future(rf, db):
    now = timezone.now()
    question1 = Question.objects.create(question_text="Question 1", pub_date=now)
    question2 = Question.objects.create(question_text="Question 2", pub_date=now + timedelta(hours=1))

    request = rf.get('/')
    response = index_view(request)
    assert response.status_code == 200
    assert list(response.context_data['latest_question_list']) == [question1]


def test_vote_question_not_found(rf, db):
    request = rf.post('/999/vote')

    with pytest.raises(Http404):
        vote(request, 999)


def test_vote_question_found_no_choice(rf, db):
    now = timezone.now()
    question1 = Question.objects.create(question_text="Question 1", pub_date=now)

    request = rf.post('{}/vote'.format(question1.id))
    response = vote(request, question1.id)
    assert response.status_code == 200
    assert question1.question_text in force_text(response.content)
    assert escape("You didn't select a choice.") in force_text(response.content)


def test_vote_question_found_with_choice(rf, db):
    now = timezone.now()
    question1 = Question.objects.create(question_text="Question 1", pub_date=now)
    choice1 = Choice.objects.create(question=question1, choice_text="Choice 1", votes=0)

    request = rf.post('{}/vote'.format(question1.id), data={"choice": choice1.id})
    response = vote(request, question1.id)
    assert response.status_code == 302
    assert response.url == reverse('polls:results', args=(question1.id,))

    choice1.refresh_from_db()
    assert choice1.votes == 1


detail_view = DetailView.as_view()


def test_detail_view_question_not_found(rf, db):
    request = rf.get('/999/')

    with pytest.raises(Http404):
        detail_view(request, pk=999)


def test_detail_view_question_found(rf, db):
    now = timezone.now()
    question1 = Question.objects.create(question_text="Question 1", pub_date=now)

    request = rf.get('/{}/'.format(question1.id))

    response = detail_view(request, pk=question1.id)
    assert response.status_code == 200
    assert response.context_data['object'] == question1
    assert 'polls/detail.html' in response.template_name


results_view = ResultsView.as_view()


def test_results_view_question_not_found(rf, db):
    request = rf.get('/999/results')

    with pytest.raises(Http404):
        results_view(request, pk=999)


def test_results_view_question_found(rf, db):
    now = timezone.now()
    question1 = Question.objects.create(question_text="Question 1", pub_date=now)

    request = rf.get('/{}/results'.format(question1.id))

    response = results_view(request, pk=question1.id)
    assert response.status_code == 200
    assert response.context_data['object'] == question1
    assert 'polls/results.html' in response.template_name
