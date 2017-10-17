Pytest workshop
===============

.footer: RoPython Cluj — `Facebook <https://www.facebook.com/ropython/>`_, `Meetup.com <https://www.meetup.com/RoPython-Cluj/>`_

----

Who
===


.. class:: center

    Ionel Cristian Mărieș

    Gabriel Muj ← actual teacher

----

Workshop content
================

* preparation & setting up tox/virtualenv/django/pytest
* writing tests for django app (the tutorial polls app) while demonstrating

  .. class:: smaller

    * test discovery
    * classes vs function tests
    * assertion helpers
    * marks, skipping & xfailing
    * parametrization
    * fixtures, scoping, finalization
    * builtin fixtures overview
    * pytest-django plugin

.. class:: center fancy

    Ask anytime and anything. Ask for pauses.

-----

Django overview
===============

* Most popular, very active development
* Django does establish certain structure on projects
  but it's not written in stone (https://djangopackages.org/grids/g/microframeworks/)
* Django ain't that big:

    Django = 79k SLOC
    Flask (werkzeug+sqlalchemy+jinja2) = 82k SLOC

* Others have way has less ecosystem, less resources and stuff you can reuse

----

Running the project: virtualenv
===============================

Linux::

    $ virtualenv ve
    $ . ve/bin/activate
    $ pip install -e .
    $ python manage.py migrate
    $ python manage.py runserver

Windows (at least use `clink <http://mridgers.github.io/clink/>`_)::

    > py -mpip install virtualenv
    > py -mvirtualenv ve
    > ve\Scripts\activate.bat
    > pip install -e .
    > python manage.py migrate
    > python manage.py runserver

----

Running the project: tox
========================

http://tox.rtfd.io

Linux::

    $ pip install tox
    $ tox -- django-admin migrate
    $ tox -- django-admin runserver

Windows (at least use `clink <http://mridgers.github.io/clink/>`_)::

    > py -mpip install tox
    > tox -- django-admin migrate
    > tox -- django-admin runserver

-----

Django primer: management commands
==================================

Management commands:

Either through ``manage.py`` or ``django-admin``:

- createsuperuser
- dbshell
- dumpdata
- loaddata
- makemigrations / migrate / showmigrations
- shell
- startapp / startproject
- runserver

------

Django primer: models
=====================

.. class:: center

    .. image:: models-wt.svg
        :height: 400


.. sourcecode:: python

    from django.db import models


    class Question(models.Model):
        question_text = models.CharField(max_length=200)
        pub_date = models.DateTimeField('date published')

-----

Quick interlude: model magic
============================

Ultra-simplified guts of Model/Form classes:

.. sourcecode:: python

    class Field:
        def __repr__(self):
            return 'Field(name={.name})'.format(self)

    class Metaclass(type):
        def __new__(mcs, name, bases, attrs):
            fields = attrs.setdefault('fields', [])
            for name, value in attrs.items():
                if isinstance(value, Field):
                    value.name = name; fields.append(value)
            return super(Metaclass, mcs).__new__(mcs, name, bases, attrs)

    class Model(metaclass=Metaclass):
        a = Field()
        b = Field()


.. sourcecode:: pycon

    >>> print(MyModel.fields)
    [Field(name=a), Field(name=b)]

-----

Django primer: views
====================

Views - two kinds:

#. Class-Based Views

   .. code-block:: py

        class DetailView(generic.DetailView):
            model = Question
            template_name = 'polls/detail.html'

#. Function views

   .. code-block:: py

        def vote(request, question_id):
            question = get_object_or_404(Question, pk=question_id)
            try:
                selected_choice = question.choice_set.get(pk=request.POST['choice'])
            except (KeyError, Choice.DoesNotExist):
                return render(request, 'polls/detail.html', {
                    'question': question,
                    'error_message': "You didn't select a choice.",
                })
            else:
                selected_choice.votes += 1
                selected_choice.save()
                return redirect('polls:results', question.id)
-----

Django primer: URLs
===================

Views are mapped to URLs in ``urls.py`` files, eg:

* ``mysite/urls.py``:

  .. code-block:: py

    urlpatterns = [
        url(r'^', include('polls.urls')),
    ]
* ``polls/urls.py``:

  .. code-block:: py

    urlpatterns = [
        url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
        url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
    ]

-----

Django primer: templates
========================

Templates automatically call and ignore missing attributes:

- ``{{ foo.bar.missing }}`` outputs nothing
- ``{{ foo }}`` calls foo if it's a callable (__call__)
- ``{{ foo(1, 2, 3) }}`` is not allowed (by design)
- ``{{ foo|default:"}}" }}`` is not possible (parser ain't very smart)

.. code-block:: html+django

    <h1>{{ question.question_text }}</h1>

    {% if error_message %}<p><strong>{{ error_message }}</strong></p>{% endif %}

    <form action="{% url 'polls:vote' question.id %}" method="post">
    {% csrf_token %}
    {% for choice in question.choice_set.all %}
        <input type="radio" name="choice" id="choice{{ forloop.counter }}" value="{{ choice.id }}" />
        <label for="choice{{ forloop.counter }}">{{ choice.choice_text }}</label><br />
    {% endfor %}
    <input type="submit" value="Vote" />
    </form>

----


Tests
=====

Some background:

- Django comes with own testing system, but it turns out ``unittest.TestCase`` ain't so good (in general).
    - There are three alternatives:

  - Nose (unmaintained)
  - Nose2 (unusable, it's missing almost all the Nose plugins)
  - Pytest

  Note that Nose is a fork of Pytest 0.8 (ancient, circa 2007)

------

Key features of pytest
======================

Different way of test setup:

- Unittest uses setup/teardown methods. Inevitably that leads to multiple inheritance and mixins.
- Pytest uses composability and DI (dependency injection)

Different way of doing assertions:

- Unittest uses assertion methods. An army of ``assertThis`` and ``assertThat``.
- Pytest uses simple assertions.

------

Key features of pytest
======================

Different way of customizing behavior:

- Unittest makes it hard to customize collection, output and other handling. You end up subclassing and monkeypatching things.
- Pytest gives you hooks to customize almost anything. And it has builtin support for markers, selection, parametrization etc.

Note: there is some support for ``unittest.TestCase`` in pytest.

------

Pytest basics
=============

Install it::

    $ pip install pytest

Make a ``tests\test_example.py``:

.. sourcecode:: python

    def test_simple():
        a = 1
        b = 2
        assert a + b == 3
        assert a + b == 4

-----

Pytest basics
=============

::

    $ pytest tests/
    ========================= test session starts ==========================
    platform linux -- Python 3.6.2, pytest-3.2.2, py-1.4.34, pluggy-0.4.0 --
    plugins: django-3.1.2
    collected 1 item

    tests/test_example.py F
    =============================== FAILURES ===============================
    _____________________________ test_simple ______________________________

        def test_simple():
            a = 1
            b = 2
            assert a + b == 3
    >       assert a + b == 4
    E       assert (1 + 2) == 4

    tests/test_example.py:5: AssertionError
    ======================= 1 failed in 0.05 seconds =======================

-----

Pytest basics
=============

Useful option and defaults, use ``pytest.ini`` for them:

.. sourcecode:: ini

    [pytest]
    ; now we can just run `pytest` instead of `pytest tests/`
    testpaths = tests

    ; note that `test_*.py` and `*_test.py` are defaults
    python_files =
        test_*.py
        *_test.py
        tests.py
    addopts =
    ; extra verbose
        -vv

    ; show detailed test counts
        -ra

    ; stop after 10 failures
        --maxfail=10

    ; subjective, I like old-school tracebacks
        --tb=short

-----

Quick interlude: imports
========================

Import system uses a list of paths (``sys.path``) to lookup.

CWD is implicitly added to ``sys.path``.

There is a module/package distinction.

Versioned imports ain't supported.

If ``sys.path = ["/var/foo", "/var/bar"]`` then:

.. class:: small

    - ``/var/foo/module.py`` - a module
    - ``/var/foo/package/__init__.py`` - a package (``import package``)
    - ``/var/foo/package/module.py`` - a module inside a package (``from package import module``)
    - ``/var/bar/module.py`` - can't be imported, it's shadowed
    - ``/var/bar/package/extra.py`` - can't be imported, its package is shadowed

Presenter notes
---------------

Bonus: namespace packages, more madness!

Python 3 native support (`PEP-420 <https://www.python.org/dev/peps/pep-0420/>`_):

- nspackages are directories paths without ``__init__.py``
- considered only after looking for package in all the paths in ``sys.path``

Python 2 ... a pile of hacks.

-----

Pytest: test collection
=======================

Pytest has a file-based test collector:

- you give it a path
- it finds all the ``test_*.py`` files
- it messes up ``sys.path`` a bit: adds all the test roots into it

Suggested layout (flat, ``tests`` ain't a package, but everything in it is)::

    tests/
    |-- foo\
    |   |-- __init__.py
    |   `-- test_foo.py
    `-- test_bar.py

Presenter notes
---------------

You can also stick the tests inside your code but that's more suited if:

- want to check that your deployed app works on unknown target platform,

  or you're targeting way too many platforms and want to offload some of the testing to users
- tests don't do crazy stuff (eating lots of resources, borking the os or leaving garbage)

-----

Pytest: fixtures
================

Not to be confused with (data) `fixtures <https://docs.djangoproject.com/en/1.11/howto/initial-data/>`_ from
Django (the result of ``dumpdata`` command).

.. sourcecode:: python

    @pytest.fixture
    def myfixture(request):
        # do some setup
        yield [1, 2, 3]
        # do some teardown

    @pytest.fixture
    def mycomplexfixture(request, fixture1, fixture2):
        pass

    def test_fixture(myfixture):
        assert myfixture == [1, 2, 3]

    def test_complexfixture(mycomplexfixture):
        pass

-----

Quick interlude: simple DI impl.
================================

.. sourcecode:: python

    import functools, inspect
    REGISTRY = {}
    def dependency(func):
        REGISTRY[func.__name__] = func
    def inject(func):
        sig = inspect.signature(func)
        for arg in sig.parameters:
            func = functools.partial(func, REGISTRY[arg]())
        return func

    @dependency
    def dep1():
        return 123
    @dependency
    def dep2():
        return 345
    @inject
    def fn(dep1, dep2):
        print(dep1, dep2)

.. sourcecode:: pycon

    >>> fn()
    123 345

-----

Pytest basics: fixture scoping
==============================

.. sourcecode:: python

    @pytest.fixture(scope="function", autouse=False)
    def myfixture(request):
        ...

``scope`` controls when and for how long the fixture is alive:

* ``scope="function"`` - default, fixture is created and teared down for every test.
* ``scope="module"`` - fixture is created for every module.
* ``scope="session"`` - fixture is created once.

``autouse`` is for situations where you don't want to explicitly request the fixture for every test.

------

Pytest: markers
===============

Are applied using decorators, eg:

.. sourcecode:: python

    @pytest.mark.skipif('platform.system() == "Windows"')
    def test_nix_stuff():
        ...

    @pytest.mark.mymark
    def test_stuff():  # can select this later by runing pytest -m mymark
        ...

    @pytest.mark.xfail('platform.system() == "Windows"', strict=True)
    def test_shouldnt_work_on_windows():  # fail if it passes
        ...

    @pytest.mark.skip
    def test_deal_with_it_later():
        ...

-----

Pytest: helpers
===============

An alternative to the ``skip`` marker:

.. sourcecode:: python

    def test_deal_with_it_later():
        pytest.skip()

An alternative to the ``skipif`` marker (sometimes):

.. sourcecode:: python

    def test_linux_stuff():
        pytest.importorskip('signalfd')

The ``raises`` context manager:

.. sourcecode:: python

    def test_stuff():
        with raises(TypeError, match='Expected FooBar, not .*!'):
            raise TypeError('Expected FooBar, not asdf!')

        with raises(TypeError) as exc_info:
            raise TypeError('Expected FooBar, not asdf!')
        assert exc_info.value.startswith('Expected FooBar')

-----

Pytest: parametrization
=======================

.. sourcecode:: python

    @pytest.mark.parametrize(['a', 'b'], [
        (1, 2),
        (2, 1),
    ])

    def test_param(a, b):
        assert a + b == 3

::

    collected 2 items

    tests/test_param.py::test_param[1-2] PASSED
    tests/test_param.py::test_param[2-1] PASSED

-----

Pytest: parametrized fixtures
=============================

.. sourcecode:: python

    @pytest.fixture(params=[len, max])
    def func(request):
        return request.param

    @pytest.mark.parametrize('numbers', [
        (1, 2),
        (2, 1),
    ])
    def test_func(numbers, func):
        assert func(numbers) == 2

::

    tests/test_param.py::test_func[func0-numbers0] PASSED
    tests/test_param.py::test_func[func0-numbers1] PASSED
    tests/test_param.py::test_func[func1-numbers0] PASSED
    tests/test_param.py::test_func[func1-numbers1] PASSED

-----

Pytest: parametrized fixtures
=============================

.. sourcecode:: python

    @pytest.fixture(params=[len, max],
                    ids=['len', 'max'])
    def func(request):
        return request.param

    @pytest.mark.parametrize('numbers', [
        (1, 2),
        (2, 1),
    ], ids=["white", "black"])
    def test_func(numbers, func):
        assert func(numbers)

::

    tests/test_param.py::test_func[len-white] PASSED
    tests/test_param.py::test_func[len-black] PASSED
    tests/test_param.py::test_func[max-white] PASSED
    tests/test_param.py::test_func[max-black] PASSED

-----

Pytest: test selection
======================

We can select tests based on the parametrization::

    $ pytest -k white -v

::

    ========================= test session starts ==========================
    platform linux -- Python 3.6.2, pytest-3.2.2, py-1.4.34, pluggy-0.4.0 --
    cachedir: .cache
    plugins: django-3.1.2
    collected 9 items

    tests/test_example.py::test_func[sum-white] PASSED
    tests/test_example.py::test_func[len-white] PASSED
    tests/test_example.py::test_func[max-white] PASSED
    tests/test_example.py::test_func[min-white] PASSED

    ========================== 5 tests deselected ==========================
    ================ 4 passed, 5 deselected in 0.07 seconds ================

-----

Pytest: hooks
=============

For now ... all you need to know about hooks:

- you can implement hooks in a ``conftest.py`` or a pytest plugin
- you put ``conftest.py`` files alongside your tests
- if there's a function that starts with ``pytest_`` - it's probably a hook.

Also, you put fixtures in your ``conftest.py`` (to use them in multiple test files)

We can talk all day long about hooks but we have to write those tests!

------

Pytest and Django
=================

Install the plugin::

    $ pip install pytest-django

Unfortunately it doesn't go through ``manage.py`` so we need to specify the settings module in ``pytest.ini``:

.. sourcecode:: ini

    [pytest]
    DJANGO_SETTINGS_MODULE = mysite.settings

------

