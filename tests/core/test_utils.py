from modernrpc.helpers import ensure_sequence


def test_ensure_sequence_1():

    assert ensure_sequence([1, 2, 3]) == [1, 2, 3]
    assert ensure_sequence(('a', 'b', 'c')) == ('a', 'b', 'c')


def test_ensure_sequence_2():

    assert ensure_sequence('str') == ['str']
    assert ensure_sequence(666) == [666]
    assert ensure_sequence({'x': 42}) == [{'x': 42}]
