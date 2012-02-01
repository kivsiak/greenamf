# -*- coding: utf-8 -*-

__author__ = 'kivsiak@gmail.com'
import inspect
#передалть в генератор
def getExposed(module):
    result = []
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj)  and hasattr(obj, 'amf_alias'):
            result.append((obj, getattr(obj, 'amf_alias')))
    return  result
