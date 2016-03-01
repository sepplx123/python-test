#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)


""" Modul mit wichtigen Funktionen zur Fibonacci-Folge """

def fib(n):
    """ Iterative Fibonacci-Funktion """
    a, b = 0, 1
    for i in range(n):
        a, b = b, a + b
    return a


def fiblist(n):
    """ produziert Liste der Fibo-Zahlen """
    fib = [0,1]
    for i in range(1,n):
        fib += [fib[-1]+fib[-2]]
    return fib


def fibratio_norm():
    """ Normal Fibonacci Ratios  (Maybe also 0.764) """
    fibratio_n = [0.0, 0.236, 0.382, 0.500, 0.618, 0.786,
                  1.000, 1.272, 1.382, 1.618,
                  2.000, 2.618,
                  4.236,
                  6.860
                  ]
    return fibratio_n


def fibratio_ext():
    """ Extendend Fibonacci Ratios """
    fibratio_e = [0.0, 0.146, 0.236, 0.382, 0.500, 0.618, 0.764, 0.786, 0.887,
                  1.000, 1.146, 1.236, 1.272, 1.382, 1.500, 1.618, 1.786, 1.887,
                  2.000, 2.618,
                  4.236,
                  6.860
                  ]
    return fibratio_e


def take_closest(_list, _value):
    """ This code will give you the closest number to "_value" in the given "_list". """
    _temp = []
    _index = 0
    
    for item in _list:
        _temp.append(abs(_value - item))
        
    _index = _temp.index(min(_temp))
    return _list[_index]


def check_fibratio(wave_1, wave_2):    
    """ Checks Fibonacci Ratios between 2 waves:  wave_1 / wave_2

        result formating:  [ result, best_fit_fibratio_n, discrepancy, best_fit_fibratio_e, discrepancy ]
    """
    _result = []
    
    _result.append(round((wave_1 / wave_2), 5))                         # calculates the exact result
    _result.append(take_closest(fibratio_norm(), _result[0]))           # calculates the closest fibratio_n
    _result.append(round(abs((_result[0]-_result[1]) * wave_1), 5))     # calculates the discrepancy in points
    _result.append(take_closest(fibratio_ext(), _result[0]))            # calculates the closest fibratio_n
    _result.append(round(abs((_result[0]-_result[3]) * wave_1), 5))     # calculates the discrepancy in points    

    #print(wave_1,wave_2,_result[0])
    return _result



############
if __name__ == "__main__":
    test_t = [2, 3, 1]
    test_p = [542.820068, 335.850097, 260.530029]

    # time ratio analysis
    # b vs a
    t = check_fibratio(test_t[1], test_t[0])
    print(t)
    # c vs b
    t = check_fibratio(test_t[2], test_t[1])
    print(t)
    # c vs a
    t = check_fibratio(test_t[2], test_t[0])
    print(t)

    # price ratio analysis
    # b vs a    
    p = check_fibratio(test_p[1], test_p[0])
    print(p)
    # c vs b    
    p = check_fibratio(test_p[2], test_p[1])
    print(p)
    # c vs a    
    p = check_fibratio(test_p[2], test_p[0])
    print(p)



























    
