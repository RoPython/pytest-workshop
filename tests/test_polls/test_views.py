import re
from datetime import timedelta

import pytest
from django.utils import timezone
from django.utils.html import escape

from polls.models import Question, Choice


@pytest.fixture
def client(client):
    func = client.request

    def wrapper(**kwargs):
        # instead of throwing prints all over the place
        print('>>>>', ' '.join('{}={!r}'.format(*item)
                               for item in kwargs.items()))
        resp = func(**kwargs)
        print('<<<<', resp, resp.content)
        # also, decode the content
        resp.text_content = resp.content.decode(resp.charset)
        return resp

    client.request = wrapper
    return client

@pytest.fixture
def question(db):
    return Question.objects.create(
        question_text="What is love?",
        pub_date=timezone.now()
    )


def test_index_view_no_question(client, db):
    response = client.get('/')
    print(type(response))
    assert response.status_code == 200
    assert list(response.context_data['latest_question_list']) == []
    # a better assertion (end-to-end style):
    assert 'No polls are available.' in response.content.decode(response.charset)
    # if you use python 2 you can just do
    assert 'No polls are available.' in response.text_content


def test_index_view_one_question(client, question):
    response = client.get('/')
    assert response.status_code == 200
    assert list(response.context_data['latest_question_list']) == [question]
    assert 'href="/polls/1/">What is love?</a>' in response.content.decode(response.charset)


@pytest.fixture
def question_factory(db):
    now = timezone.now()

    def create_question(question_text, pub_date_delta=timedelta()):
        return Question.objects.create(
            question_text=question_text,
            pub_date=now + pub_date_delta
        )

    return create_question


def test_index_view_two_questions(client, question_factory):
    question1 = question_factory("Question 1")
    question2 = question_factory("Question 2", -timedelta(hours=1))

    response = client.get('/')
    assert response.status_code == 200
    assert list(response.context_data['latest_question_list']) == [question1, question2]
    content = response.content.decode(response.charset)
    assert 'href="/polls/1/">Question 1</a>' in content
    assert 'href="/polls/2/">Question 2</a>' in content


def test_index_view_only_last_five_questions(client, question_factory):
    questions = [question_factory("Question {}".format(i), -timedelta(hours=i))
                 for i in range(1, 10)]

    response = client.get('/')
    assert response.status_code == 200
    assert list(response.context_data['latest_question_list']) == questions[:5]

    content = response.content.decode(response.charset)
    for i in range(1, 6):
        assert 'href="/polls/{0}/">Question {0}</a>'.format(i) in content
    assert 'Question 6' not in content


def test_index_view_exclude_question_published_in_future(client, question_factory):
    question_factory("Question 1", timedelta(hours=1))

    response = client.get('/')
    assert response.status_code == 200
    assert list(response.context_data['latest_question_list']) == []
    assert 'Question 1' not in response.content.decode(response.charset)


def test_vote_question_not_found(client, db):
    response = client.get('/999/vote/')
    assert response.status_code == 404


def test_vote_question_found_no_choice(client, question):
    response = client.post('/%s/vote/' % question.id)
    assert response.status_code == 200
    content = response.content.decode(response.charset)
    assert 'What is love?' in content
    assert "You didn&#39;t select a choice." in content


@pytest.fixture
def question_choice_factory(db):
    def create_question_choice(question, choice_text, votes=0):
        return Choice.objects.create(question=question, choice_text=choice_text, votes=votes)
    return create_question_choice


def test_vote_question_found_with_choice(client, question, question_choice_factory):
    choice1 = question_choice_factory(question, "Choice 1", votes=0)

    response = client.post('/%s/vote/' % question.id,
                           data={"choice": choice1.id})
    assert response.status_code == 302
    assert response.url == '/%s/results/' % (question.id,)

    choice1.refresh_from_db()
    assert choice1.votes == 1

    response = client.get('/%s/results/' % question.id)
    # assert '<li>Choice 1 -- 1 vote</li>' in response.text_content
    assert re.findall(r'<li>Choice 1\s+--\s+1 vote</li>', response.text_content, re.MULTILINE)


def test_detail_view_question_not_found(client, db):
    response = client.get('/999/')
    assert response.status_code == 404


def test_detail_view_question_found(client, question):
    response = client.get('/%s/' % question.id)
    assert response.status_code == 200
    assert 'What is love?' in response.text_content
    assert 'Someone needs to figure out some answers!' in response.text_content

    # assertions you'll be sorry for (coupling!)
    assert response.context_data['object'] == question
    assert 'polls/detail.html' in response.template_name


def test_results_view_question_not_found(client, db):
    response = client.get('/999/results/')
    assert response.status_code == 404


def test_results_view_question_found(client, question):
    response = client.get('/%s/results/' % question.id)
    assert response.status_code == 200
    assert response.context_data['object'] == question
    assert 'polls/results.html' in response.template_name
