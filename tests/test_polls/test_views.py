from datetime import timedelta

from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.html import escape


def test_index_view_no_question(client, db):
    response = client.get('/')
    assert response.status_code == 200
    assert list(response.context_data['latest_question_list']) == []
    # a better assertion (end-to-end style):
    assert 'No polls are available.' in response.content.decode(response.charset)
    # if you use python 2 you can just do
    assert 'No polls are available.' in response.content


def test_index_view_one_question(client, question):
    response = client.get('/')
    assert response.status_code == 200
    assert list(response.context_data['latest_question_list']) == [question]
    assert 'href="/polls/1/">What is love?</a>' in response.content.decode(response.charset)


def test_index_view_two_questions(client, question_generator):
    now = timezone.now()
    question1 = question_generator(question_text="Question 1", pub_date=now)
    question2 = question_generator(question_text="Question 2", pub_date=now - timedelta(hours=1))

    response = client.get('/')
    assert response.status_code == 200
    assert list(response.context_data['latest_question_list']) == [question1, question2]


def test_index_view_only_last_five_questions(client, question_generator):
    now = timezone.now()
    questions = [question_generator(question_text="Question {}".format(i), pub_date=now - timedelta(hours=i))
                 for i in range(0, 10)]

    response = client.get('/')
    assert response.status_code == 200
    assert list(response.context_data['latest_question_list']) == questions[:5]


def test_index_view_exclude_question_published_in_future(client, question_generator):
    now = timezone.now()
    question1 = question_generator(question_text="Question 1", pub_date=now)
    question2 = question_generator(question_text="Question 2", pub_date=now + timedelta(hours=1))

    response = client.get('/')
    assert response.status_code == 200
    assert list(response.context_data['latest_question_list']) == [question1]


def test_vote_question_not_found(client, db):
    response = client.get('/999/vote/')
    assert response.status_code == 404


def test_vote_question_found_no_choice(client, question):
    response = client.post('/%s/vote/' % question.id)
    assert response.status_code == 200
    assert question.question_text in force_text(response.content)
    assert escape("You didn't select a choice.") in force_text(response.content)


def test_vote_question_found_with_choice(client, question, question_choice_generator):
    choice1 = question_choice_generator(question=question, choice_text="Choice 1", votes=0)

    response = client.post('/%s/vote/' % question.id,
                           data={"choice": choice1.id})
    assert response.status_code == 302
    assert response.url == '/%s/results/' % (question.id,)

    choice1.refresh_from_db()
    assert choice1.votes == 1


def test_detail_view_question_not_found(client, db):
    response = client.get('/999/')
    assert response.status_code == 404


def test_detail_view_question_found(client, question):
    response = client.get('/%s/' % question.id)
    assert response.status_code == 200
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
