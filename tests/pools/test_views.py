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


def test_index_view_no_question(client, db):
    response = client.get(reverse('polls:index'))
    assert response.status_code == 200
    assert list(response.context_data['latest_question_list']) == []


def test_index_view_one_question(client, db):
    now = timezone.now()
    question1 = Question.objects.create(question_text="Question 1", pub_date=now)

    response = client.get(reverse('polls:index'))
    assert response.status_code == 200
    assert list(response.context_data['latest_question_list']) == [question1]


def test_index_view_two_questions(client, db):
    now = timezone.now()
    question1 = Question.objects.create(question_text="Question 1", pub_date=now)
    question2 = Question.objects.create(question_text="Question 2", pub_date=now - timedelta(hours=1))

    response = client.get(reverse('polls:index'))
    assert response.status_code == 200
    assert list(response.context_data['latest_question_list']) == [question1, question2]


def test_index_view_only_last_five_questions(client, db):
    now = timezone.now()

    questions = []
    for i in range(0, 10):
        questions.append(Question.objects.create(
            question_text="Question {}".format(i), pub_date=now - timedelta(hours=i)
        ))

    response = client.get(reverse('polls:index'))
    assert response.status_code == 200
    assert list(response.context_data['latest_question_list']) == questions[:5]


def test_index_view_exclude_question_published_in_future(client, db):
    now = timezone.now()
    question1 = Question.objects.create(question_text="Question 1", pub_date=now)
    question2 = Question.objects.create(question_text="Question 2", pub_date=now + timedelta(hours=1))

    response = client.get(reverse('polls:index'))
    assert response.status_code == 200
    assert list(response.context_data['latest_question_list']) == [question1]


def test_vote_question_not_found(client, db):
    response = client.get(reverse('polls:vote', kwargs={"question_id": 999}))
    assert response.status_code == 404


def test_vote_question_found_no_choice(client, db):
    now = timezone.now()
    question1 = Question.objects.create(question_text="Question 1", pub_date=now)

    response = client.post(reverse('polls:vote', kwargs={"question_id": question1.id}))
    assert response.status_code == 200
    assert question1.question_text in force_text(response.content)
    assert escape("You didn't select a choice.") in force_text(response.content)


def test_vote_question_found_with_choice(client, db):
    now = timezone.now()
    question1 = Question.objects.create(question_text="Question 1", pub_date=now)
    choice1 = Choice.objects.create(question=question1, choice_text="Choice 1", votes=0)

    response = client.post(reverse('polls:vote', kwargs={"question_id": question1.id}),
                           data={"choice": choice1.id})
    assert response.status_code == 302
    assert response.url == reverse('polls:results', args=(question1.id,))

    choice1.refresh_from_db()
    assert choice1.votes == 1


detail_view = DetailView.as_view()


def test_detail_view_question_not_found(client, db):
    response = client.get(reverse('polls:detail', kwargs={"pk": 999}))
    assert response.status_code == 404


def test_detail_view_question_found(client, db):
    now = timezone.now()
    question1 = Question.objects.create(question_text="Question 1", pub_date=now)

    response = client.get(reverse('polls:detail', kwargs={"pk": question1.id}))
    assert response.status_code == 200
    assert response.context_data['object'] == question1
    assert 'polls/detail.html' in response.template_name


results_view = ResultsView.as_view()


def test_results_view_question_not_found(client, db):
    response = client.get(reverse('polls:results', kwargs={"pk": 999}))
    assert response.status_code == 404


def test_results_view_question_found(client, db):
    now = timezone.now()
    question1 = Question.objects.create(question_text="Question 1", pub_date=now)

    response = client.get(reverse('polls:results', kwargs={"pk": question1.id}))
    assert response.status_code == 200
    assert response.context_data['object'] == question1
    assert 'polls/results.html' in response.template_name
