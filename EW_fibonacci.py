#!/usr/bin/python
# -*- coding: utf-8 -*-

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
    """ Normal Fibonacci Ratios """
    fibratio_n = (0.0, 0.236, 0.382, 0.500, 0.618, 0.786,
                  1.000, 1.272, 1.382, 1.618,
                  2.000, 2.618,
                  4.236,
                  6.860
                  )
    return fibratio_n


def fibratio_ext():
    """ Extendend Fibonacci Ratios """
    fibratio_e = (0.0, 0.146, 0.236, 0.382, 0.500, 0.618, 0.786, 0.887,
                  1.000, 1.146, 1.236, 1.272, 1.382, 1.500, 1.618, 1.786, 1.887,
                  2.000, 2.618,
                  4.236,
                  6.860
                  )
    return fibratio_e

    
