
def func_a():
    """
    Does nothing...

    """
    pass


def func_b():
    """
    Not very useful, but...

    """
    pass


def func_c():
    """
    May be improved in the future...

    """
    pass


def full_documented_method(name, birth_date, sex):
    """
    This is the textual doc of the method
    :param name: A name
    :param birth_date: A birth date
    :param sex: Male or Female
    :type name: str
    :type birth_date: datetime.datetim
    :type sex: str
    :return: A string representation of given arguments
    """
    return '{} ({}) born on {}'.format(name, str(sex), str(birth_date))
