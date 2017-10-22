import pytest


@pytest.fixture(params=[len, max],
                ids=['len', 'max'])
def func(request):
    return request.param

@pytest.mark.parametrize('numbers', [
    (1, 2),
    (2, 1),
], ids=["white", "black"])
@pytest.mark.custom
def test_func(numbers, func):
    assert func(numbers)
