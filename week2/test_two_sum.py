from two_sum import two_sum


def test_simple_pair():
    assert two_sum([2, 7, 11, 15], 9) == [0, 1]


def test_pair_not_at_the_front():
    assert two_sum([3, 2, 4], 6) == [1, 2]


def test_repeated_value():
    assert two_sum([3, 3], 6) == [0, 1]


def test_no_pair_returns_empty():
    assert two_sum([1, 2, 3], 100) == []
