# -*- coding: utf-8 -*-

"""
This file is part of Magpie OnlineJudge Project
Authors: DarcJC
"""


class LazyProperty:
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            value = self.func(instance)
            setattr(instance, self.func.__name__, value)
            return value


def final_lazy_property(func):
    """
    lazy property that not modifiable
    :param func:
    :return:
    """
    name = '_lazy_' + func.__name__
    @property
    def lazy(self):
        if hasattr(self, name):
            return getattr(self, name)
        else:
            value = func(self)
            setattr(self, name, value)
            return value
    return lazy
