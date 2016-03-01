#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import sys

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from matplotlib.dates import datestr2num

import matplotlib.ticker as mticker
from matplotlib.finance import candlestick_ohlc, candlestick2_ohlc
from matplotlib import style

import numpy as np
import urllib2
import datetime as dt
import csv


import EW_fibonacci
import EW_testtool_V01



def check_lower(value_1,value_2):
    """ checks if value_1 is lower than value_2 and when the result is True
        it returns True, otherwise False """
    if abs(value_1 / value_2) < 1:
        return True
    else:
        return False

def check_higher(value_1,value_2):
    """ checks if value_1 is higher than value_2 and when the result is True
        it returns True, otherwise False """
    if abs(value_1 / value_2) > 1:
        return True
    else:
        return False

def check_in_range(value, lim_1, lim_2):
    """ checks if the value is higher than lo_lim and lower than hi_lim.
        when the result is True, it returns True otherwise False """
    lo_lim = min(lim_1, lim_2)
    hi_lim = max(lim_1, lim_2)
    
    if (abs(value) > abs(lo_lim) and abs(value) < abs(hi_lim)):
        return True
    else:
        return False

def check_out_range(value, lim_1, lim_2):
    """ checks if the value is higher than hi_lim or lower than lo_lim.
        when the result is True, it returns True otherwise False """
    lo_lim = min(lim_1, lim_2)
    hi_lim = max(lim_1, lim_2)
    
    if abs(value) > abs(hi_lim) or abs(value) < abs(lo_lim):
        return True
    else:
        return False



"""
The following Formations are possible respectively in bear and bull direction:
        - Impulse (12345)
        - Leading_Diagonal (12345)
        - Ending_Diagonal (12345)
        - ABC_Correction (ABC)
        - Triangle (5 Waves ABCDE)
        - Triangle (9 Waves ABCDEFGHI)
        - Double_Combo (WXY)
        - Triple_Combo (WXYXZ)


Elliott Wave Degrees:
        - Grand Sypercycle: Centuries to Millenia
        - Supercycle: multi-decade (about 40–70 years)
        - Cycle: one year to several years (or even several decades under an Elliott Extension)
        - Primary: Quaters to years
        - Intermediate: Months to years
        - Minor: Months to Quaters
        - Minute: Weeks to Quaters
        - Minuette: Weeks to Months
        - Subminuette: Days to Months
        - Micro: Days to Weeks
        - Sub-Micro: Half-Days to Days
        - Mil: Hours to Half-Days
        - Sub-Mil: Minutes to Quater Days
        - Nano: Minutes to Hours
        - Sub-Nano: Seconds to Minutes
"""
################################       
################################
################################
class ABC_Correction():
    """
    Zigzag, Flat, Running Flat, Expanding Flat
    """
    
    def __init__(self):
        """
        """
        self.results = []

    def check(self, data_input):
        """
        data_input          = [] # [ [time_values], [price_values] ]

        The check method consists of 2 parts: time- and price-ratio check
        check procedure: b_a (b vs a), c_b (c vs b), c_a (c vs a)
        
        EW_fibonacci.check_fibratio(wave_1, wave_2):

        lvl_1_waves_results = [] # [ [{"wave2_wave1_t" : result, best_fit_fibratio_n, precision, best_fit_fibratio_e, precision}, # time analysis
                                      {"wave2_wave1_p" : result, best_fit_fibratio_n, precision, best_fit_fibratio_e, precision}, # price analysis
                                     ]
                                     [{"wave3_wave2_t" : result, best_fit_fibratio_n, precision, best_fit_fibratio_e, precision}, # time analysis
                                      {"wave3_wave2_p" : result, best_fit_fibratio_n, precision, best_fit_fibratio_e, precision}, # price analysis
                                     ]
                                     [{"wave3_wave1_t" : result, best_fit_fibratio_n, precision, best_fit_fibratio_e, precision}, # time analysis
                                      {"wave3_wave1_p" : result, best_fit_fibratio_n, precision, best_fit_fibratio_e, precision}, # price analysis
                                     ]
                                     valid pattern found (True/False)
                                     ["pattern1","pattern2",... ]
                                   ]        
        """
        self.results = [ [], [], [], False, [] ]
        _result = {}
        _wave1_t = data_input[0][0]
        _wave2_t = data_input[0][1]
        _wave3_t = data_input[0][2]        
        _wave1_p = data_input[1][0]
        _wave2_p = data_input[1][1]
        _wave3_p = data_input[1][2]

        #Step1:   b vs a
        #Step1.1: time_analaysis
        _result = {}        
        _result[str("b_a_t")]  = EW_fibonacci.check_fibratio(_wave2_t, _wave1_t)
        self.results[0].append(_result)

        #Step1.2: price_analaysis
        _result = {}     
        _result[str("b_a_p")]  = EW_fibonacci.check_fibratio(_wave2_p, _wave1_p)
        self.results[0].append(_result)


        #Step2:   c vs b
        #Step2.1: time_analaysis
        _result = {}              
        _result[str("c_b_t")]  = EW_fibonacci.check_fibratio(_wave3_t, _wave2_t)
        self.results[1].append(_result)

        #Step2.2: price_analaysis
        _result = {}              
        _result[str("c_b_p")]  = EW_fibonacci.check_fibratio(_wave3_p, _wave2_p)
        self.results[1].append(_result)

        
        #Step3:   c vs a
        #Step3.1: time_analaysis
        _result = {}        
        _result[str("c_a_t")]  = EW_fibonacci.check_fibratio(_wave3_t, _wave1_t)
        self.results[2].append(_result)

        #Step3.2: price_analaysis
        _result = {}        
        _result[str("c_a_p")]  = EW_fibonacci.check_fibratio(_wave3_p, _wave1_p)
        self.results[2].append(_result)


        #Step4: Check if this a-b-c is valid or not and which pattern can be chosen
        self.results[3], self.results[4] =  self.check_type(data_input)


        #Step5: return the results
        return self.results



###########################################################################
    def check_type(self,data_input):
        """
        data_input          = [] # [ [time_values], [price_values] ]
        
        possible types are: Zigzag, Flat, R_Flat, E_Flat
        """
        _type = []
        
        if self.zigzag(data_input): _type.append(str("zigzag"))
        if self.flat(data_input):   _type.append(str("flat"))       
        if self.r_flat(data_input): _type.append(str("r_flat"))       
        if self.e_flat(data_input): _type.append(str("e_flat"))        
        #print('_type:',_type)

        if _type:
            return True, _type
        else:
            return False, _type
            

    def zigzag(self,data_input):
        """
        Zigzag
        Bei einem einfachen Zigzag besteht die innere Struktur aus 3 Wellen (a, b, c) 5-3-5.
            Rules:
                1. Die Welle a muss ein Impuls oder ein Leading Diagonal Triangle(LDT) sein.
                2. Die Welle b muss ein beliebiges Korrekturmuster aufweisen.
                3. Die Welle b korrigiert die Welle a nicht mehr als 99 %.
                4. Die Welle c muss ein Impuls oder ein Ending Diagonal Triangle (EDT) sein.
                5. Die Welle c muss aus preislicher Sicht mindestens 70 % der Welle b betragen.
                6. Die Welle c versagt äußerst selten.
                7. Die Welle c wird nicht länger als 261,8 % der Welle a.
                
            Guidelines:
                1. Die Welle b korrigiert häufig weniger als 61,8 % der Welle a,
                insgesamt sind Korrekturen von 1% – 99 % erlaubt.
                2. Die Welle b ist eine Korrekturwelle und kann sich als Zigzag, Flat,
                Dreieck oder als Variation dieser Muster ausbilden.
                3. Wenn ein Segment der Welle b mehr als 61,8 % die Welle a korrigiert,
                dann ist davon auszugehen, dass sich eine komplexere Korrektur ausbilden wird.
                Die Welle c muss deswegen bevorzugt über das Ende der Welle a hinausgehen.
                4. Die Welle c und die Welle a sind häufig gleich lang.
                5. Das Längenverhältnis zwischen Welle a und c beträgt häufig 61,8% - 100%
                und maximal 261,8 % der Welle a.
                6. Wird die Welle c steiler als die Welle a, dann muss eine Fortsetzung
                der Korrektur in Form eines Double- oder Triple-Zigzags oder andere Kombinationen erwartet werden.
                7. Wird die Welle c länger als 161,8 % der Welle a, sollte man statt a, b, c
                Korrektur eher auf eine Impulszählung 1, 2 und 3 umstellen.
                8. In einem Zigzag kann die Welle b aus einem Flat, Zigzag, Triangle,
                DoubleZigzag, Triple-Zigzag, Double-Three und einem Triple-Three gebildet werden.
                9. Die 0 - b Linie wird nur selten verletzt. Verletzungsgefahr besteht,
                wenn sich die Welle c als EDT ausbildet.
                10. Ein Zigzag ist eine eigenständige Korrektur und kann das Ende einer Korrektur sein.
                Es kann sich aber mit einer anderen Standartkorrekturform kombinieren (Zigzag, Flat oder Triangle).
        """
        _result = []
        _temp = 0
        _offset = 0.05        
        _wave1_t = data_input[0][0]
        _wave2_t = data_input[0][1]
        _wave3_t = data_input[0][2]        
        _wave1_p = data_input[1][0]
        _wave2_p = data_input[1][1]
        _wave3_p = data_input[1][2]

        _result.append(check_lower(_wave2_p, _wave1_p))                    # Rule 3
        _result.append(check_higher((_wave3_p / _wave2_p), 0.7))           # Rule 5
        _result.append(check_lower((_wave3_p / _wave1_p), 2.618+_offset))  # Rule 7
        
        #print('_result:', _result)
        _temp = [item for item in _result if item]

        # Only if all conditons are True the pattern is valid
        if len(_temp) == len(_result):
            return True
        else:
            return False

    def flat(self,data_input):
        """
        Flat
        Bei einem einfachen Flat besteht die innere Struktur aus 3 Wellen (a, b, c) 3-3-5.
    
        Rules:
            1. Die Welle a muss ein beliebiges Korrekturmuster aufweisen, außer
            einem Triangle.
            2. Die Welle b muss ein beliebiges Korrekturmuster aufweisen.
            3. Die Welle b muss mindestens 38,2 % der Welle a korrigieren.
            4. Die Welle b ist in einem normalen Flat nicht länger als die Welle a.
            5. Die Welle c muss ein Impuls oder ein Ending Diagonal Triangle (EDT)
            sein.
            6. Die Welle c muss aus preislicher Sicht mindestens 61,8 % der Welle a
            betragen.
            7. Die Welle c wird nicht länger als 261,8 % der Welle a.

        Guidelines:
            1. Die Welle a ist häufig ein Zigzag, Double- oder Triple-Zigzag.
            2. Die Welle b korrigiert oft 61,8 % der Welle a, eher bis 100 %.
            3. Die Welle c und die Welle a sind häufig gleich lang. Oft liegt der
            Endpunkt der Welle c am Endpunkt der Welle a.
            4. Das Längenverhältnis zwischen Welle a und c beträgt häufig 61,8 % bis
            100 % und sehr selten mehr als 161,8 % der Welle a.
            5. Die Welle b ist zeitlich gesehen oft doppelt so lang wie Welle a.
            6. Entsteht eine komplexe Welle a, so ist davon auszugehen, dass sich Welle b und
            c zusammen zeitlich wie Welle a ausbilden.
            7. Das Flat kann selber als Korrekturmuster stehen, aber auch zusätzlich mit
            Standard-Formen wie ein zweites Flat, Zigzag oder Triangle kombiniert werden.
            8. Wird die Welle c steiler als die Welle a, dann muss mit einer komplexeren
            Korrektur gerechnet werden.
            9. In einem Zigzag kann die Welle b aus einem Flat, Zigzag, Triangle, DoubleZigzag,
            Triple-Zigzag, Double- Three und einem Triple- Three gebildet werden.
        """
        _result = []
        _temp = 0
        _offset = 0.05
        _wave1_t = data_input[0][0]
        _wave2_t = data_input[0][1]
        _wave3_t = data_input[0][2]        
        _wave1_p = data_input[1][0]
        _wave2_p = data_input[1][1]
        _wave3_p = data_input[1][2]

        _result.append(check_higher((_wave2_p / _wave1_p), 0.382))          # Rule 3
        _result.append(check_lower(_wave2_p, _wave1_p))                     # Rule 4
        _result.append(check_higher((_wave3_p / _wave1_p), 0.618))          # Rule 6        
        _result.append(check_lower(_wave3_p / _wave1_p, 2.618+_offset))     # Rule 7
        
        #print('_result:', _result)
        _temp = [item for item in _result if item]

        # Only if all conditons are True the pattern is valid
        if len(_temp) == len(_result):
            return True
        else:
            return False

    def r_flat(self,data_input):
        """
        Running Flat
        Rules:
            1. Die Welle a muss ein beliebiges Korrekturmuster aufweisen, außer einem Triangle.
            2. Die Welle b muss ein beliebiges Korrekturmuster aufweisen.
            3. Die Welle b ist länger als die Welle a.
            4. Die Welle c ist kleiner als die Welle b.
            5. Die Welle c muss ein Impuls oder ein Ending Diagonal Triangle (EDT) sein.
            6. Der Endpunkt der Welle c liegt in der Preisspanne der Welle a.

        Guidelines:
            1. Die Welle a ist häufig ein Zigzag, Double- oder Triple-Zigzag.
            2. Die Welle b ist oft zeitlich gesehen ca. doppelt so lang wie Welle a.
            3. Die Welle b ist eine Korrekturwelle und kann sich als Zigzag, Flat,
            Dreieck oder als Variation dieser Muster ausbilden.
            4. Die Welle b korrigiert häufig 101 % bis 161,8 % der Welle a.
            5. Die Welle c erreicht häufig mindestens 61,8 % bis 100 % der Welle a.
            6. Entsteht eine komplexe Welle a, so ist davon auszugehen, dass sich
            Welle b und c zusammen zeitlich wie Welle a ausbilden.
            7. Das Running Flat steht hauptsächlich selber als Korrekturmuster, wird
            aber (sehr selten) zusätzlich mit Standard-Formen wie ein zweites Flat,
            Zigzag oder Triangle kombiniert auftreten.
        """
        _result = []
        _temp = 0
        _offset = 0.05
        _wave1_t = data_input[0][0]
        _wave2_t = data_input[0][1]
        _wave3_t = data_input[0][2]        
        _wave1_p = data_input[1][0]
        _wave2_p = data_input[1][1]
        _wave3_p = data_input[1][2]

        _result.append(check_higher(_wave2_p, _wave1_p))                     # Rule 3
        _result.append(check_lower(_wave3_p, _wave2_p))                      # Rule 4
        _result.append(check_in_range((_wave3_p - _wave2_p), 0, _wave1_p))   # Rule 6        

        
        #print('_result:', _result)
        _temp = [item for item in _result if item]

        # Only if all conditons are True the pattern is valid
        if len(_temp) == len(_result):
            return True
        else:
            return False
        

    def e_flat(self,data_input):
        """
        Expanding Flat
        Rules:
            1. Die Welle a muss ein beliebiges Korrekturmuster aufweisen, außer
            einem Triangle.
            2. Die Welle b muss ein beliebiges Korrekturmuster aufweisen.
            3. Die Welle b ist länger als die Welle a.
            4. Die Welle c ist länger als die Welle b.
            5. Die Welle c muss ein Impuls oder ein Ending Diagonal Triangle (EDT)
            sein.
            6. Der Endpunkt der Welle b und c liegt nicht in der Preisspanne der
            Welle a.

        Guidelines:
            1. Die Welle a ist häufig ein Zigzag, Double- oder Triple-Zigzag.
            2. Die Welle b ist oft zeitlich gesehen ca. doppelt so lang wie Welle a.
            3. Die Welle b ist eine Korrekturwelle und kann sich als Zigzag, Flat,
            Dreieck oder als Variation dieser Muster ausbilden.
            4. Die Welle b korrigiert häufig 101 % bis 161,8 % der Welle a.
            5. Die Welle c erreicht häufig 161,8 % bis 261,8 % der Welle a.
            6. Entsteht eine komplexe Welle a, so ist davon auszugehen, dass sich
            Welle b und c zusammen zeitlich wie Welle a ausbilden.
            7. Das Expanding Flat steht hauptsächlich für sich selber als
            Korrekturmuster, wird aber (sehr selten) zusätzlich mit Standard-Formen
            wie ein zweites Flat, Zigzag oder Triangle kombiniert auftreten.
        """
        _result = []
        _temp = 0
        _offset = 0.05
        _wave1_t = data_input[0][0]
        _wave2_t = data_input[0][1]
        _wave3_t = data_input[0][2]        
        _wave1_p = data_input[1][0]
        _wave2_p = data_input[1][1]
        _wave3_p = data_input[1][2]

        _result.append(check_higher(_wave2_p, _wave1_p))                     # Rule 3
        _result.append(check_higher(_wave3_p, _wave2_p))                     # Rule 4
                                                                             # Rule 6      Geht gar ned wegen #3 & #4 !!!  

        
        #print('_result:', _result)
        _temp = [item for item in _result if item]

        # Only if all conditons are True the pattern is valid
        if len(_temp) == len(_result):
            return True
        else:
            return False





################################       
################################
################################
class Impulse():
    """
    Impulse, extending waves
    """
    
    def __init__(self):
        """ """
        self.results = []

    def check(self, data_input):
        """
        data_input          = [] # [ [time_values], [price_values] ]

        The check method consists of 2 parts: time- and price-ratio check
        check procedure: 2_1 (2 vs 1), 3_1 (3 vs 1), 3_2 (3 vs 2), 4_2, 4_3, 5_1, 5_3, 5_0-3, 5_4
        
        EW_fibonacci.check_fibratio(wave_1, wave_2):

        _results = [] # [ [{"wave2_wave1_t" : result, best_fit_fibratio_n, precision, best_fit_fibratio_e, precision}, # time analysis
                           {"wave2_wave1_p" : result, best_fit_fibratio_n, precision, best_fit_fibratio_e, precision}, # price analysis
                          ]
                          [{"wave3_wave1_t" : result, best_fit_fibratio_n, precision, best_fit_fibratio_e, precision}, # time analysis
                           {"wave3_wave1_p" : result, best_fit_fibratio_n, precision, best_fit_fibratio_e, precision}, # price analysis
                          ]
                          [{"wave3_wave2_t" : result, best_fit_fibratio_n, precision, best_fit_fibratio_e, precision}, # time analysis
                           {"wave3_wave2_p" : result, best_fit_fibratio_n, precision, best_fit_fibratio_e, precision}, # price analysis
                          ]
                           valid pattern found (True/False)
                           ["pattern1","pattern2",... ]
                        ]        
        """
        self.results = [ [], [], [], [], [], [], [], [], [], False, [] ]
        _temp = 0
        _result = {}
        _wave1_t = data_input[0][0]
        _wave2_t = data_input[0][1]
        _wave3_t = data_input[0][2]
        _wave4_t = data_input[0][3]
        _wave5_t = data_input[0][4]        
        _wave1_p = data_input[1][0]
        _wave2_p = data_input[1][1]
        _wave3_p = data_input[1][2]
        _wave4_p = data_input[1][3]
        _wave5_p = data_input[1][4]

        #Step1:   2 vs 1
        #Step1.1: time_analaysis
        _result = {}        
        _result[str("2_1_t")]  = EW_fibonacci.check_fibratio(_wave2_t, _wave1_t)
        self.results[0].append(_result)
        
        #Step1.2: price_analaysis
        _result = {}        
        _result[str("2_1_p")]  = EW_fibonacci.check_fibratio(_wave2_p, _wave1_p)
        self.results[0].append(_result)


        #Step2:   3 vs 1
        #Step2.1: time_analaysis
        _result = {}        
        _result[str("3_1_t")]  = EW_fibonacci.check_fibratio(_wave3_t, _wave1_t)
        self.results[1].append(_result)
        
        #Step2.2: price_analaysis
        _result = {}        
        _result[str("3_1_p")]  = EW_fibonacci.check_fibratio(_wave3_p, _wave1_p)
        self.results[1].append(_result)
        

        #Step3:   3 vs 2
        #Step3.1: time_analaysis
        _result = {}        
        _result[str("3_2_t")]  = EW_fibonacci.check_fibratio(_wave3_t, _wave2_t)
        self.results[2].append(_result)
        
        #Step3.2: price_analaysis
        _result = {}        
        _result[str("3_2_p")]  = EW_fibonacci.check_fibratio(_wave3_p, _wave2_p)
        self.results[2].append(_result)       


        #Step4:   4 vs 2
        #Step4.1: time_analaysis
        _result = {}        
        _result[str("4_2_t")]  = EW_fibonacci.check_fibratio(_wave4_t, _wave2_t)
        self.results[3].append(_result)
        
        #Step4.2: price_analaysis
        _result = {}        
        _result[str("4_2_p")]  = EW_fibonacci.check_fibratio(_wave4_p, _wave2_p)
        self.results[3].append(_result) 

        #Step5:   4 vs 3
        #Step5.1: time_analaysis
        _result = {}        
        _result[str("4_3_t")]  = EW_fibonacci.check_fibratio(_wave4_t, _wave3_t)
        self.results[4].append(_result)
        
        #Step5.2: price_analaysis        
        _result = {}        
        _result[str("4_3_p")]  = EW_fibonacci.check_fibratio(_wave4_p, _wave3_p)
        self.results[4].append(_result)


        #Step6:   5 vs 1
        #Step6.1: time_analaysis
        _result = {}        
        _result[str("5_1_t")]  = EW_fibonacci.check_fibratio(_wave5_t, _wave1_t)
        self.results[5].append(_result)
        
        #Step6.2: price_analaysis
        _result = {}        
        _result[str("5_1_p")]  = EW_fibonacci.check_fibratio(_wave5_p, _wave1_p)
        self.results[5].append(_result)       

        #Step7:   5 vs 3
        #Step7.1: time_analaysis
        _result = {}        
        _result[str("5_3_t")]  = EW_fibonacci.check_fibratio(_wave5_t, _wave3_t)
        self.results[6].append(_result)
        
        #Step7.2: price_analaysis
        _result = {}        
        _result[str("5_3_p")]  = EW_fibonacci.check_fibratio(_wave5_p, _wave3_p)
        self.results[6].append(_result)
        

        #Step8:   5 vs 0-3
        #Step8.1: time_analaysis
        _result = {}        
        _result[str("5_0-3_t")]  = EW_fibonacci.check_fibratio(_wave5_t, (_wave1_t + _wave2_t +_wave3_t))
        self.results[7].append(_result)        
        
        #Step8.2: price_analaysis
        _result = {}        
        _result[str("5_0-3_p")]  = EW_fibonacci.check_fibratio(_wave5_p, (_wave1_p - _wave2_p +_wave3_p))
        self.results[7].append(_result)

        
        #Step9:   5 vs 4
        #Step9.1: time_analaysis
        _result = {}        
        _result[str("5_4_t")]  = EW_fibonacci.check_fibratio(_wave5_t, _wave4_t)
        self.results[8].append(_result)
        
        #Step9.2: price_analaysis        
        _result = {}        
        _result[str("5_4_p")]  = EW_fibonacci.check_fibratio(_wave5_p, _wave4_p)
        self.results[8].append(_result)
        

        #Step10: Check if this impulse is valid or not
        self.results[9], self.results[10] =  self.check_type(data_input)


        #Step11: return the results
        return self.results

    

    def check_type(self,data_input):
        """
        Impulse, extending waves
        Rules:
            1. Eine Impulswelle besteht aus fünf Wellen.
            2. Die Welle 1 muss ein Impuls oder ein Leading Diagonal Triangle (LDT) sein.
            3. Die Welle 2 muss ein korrektives Muster aufweisen, außer einem Dreieck.
            4. Die Welle 2 darf nicht mehr als 99,9 % der Welle 1 korrigieren
            (retracen). Das heißt, die Welle 2 darf nicht den Ursprung der Welle 1 berühren.
            5. Die Welle 3 muss ein Impuls sein.
            6. Die Welle 3 ist nie die kürzeste Welle.
            7. Die Welle 3 muss aus preislicher Sicht länger als die Welle 2 sein.
            8. Die Welle 4 muss ein korrektives Muster enthalten.
            9. Die Welle 4 darf den Preiskorridor der Welle 1 nicht überlappen. Ausnahme in einem Diagonal Triangle (EDT und LDT).
            10. Die Welle 5 muss ein Impuls oder ein Ending Diagonal Triangle sein.
            11. Die versagende Welle 5 muss aus preislicher Sicht mindestens 70 % der Welle 4 betragen.

        Guidelines:
            1. Die ausgedehnte Impulswelle erreicht sehr oft das 1,618-fache der anderen Impulswellen.
            2. Die Welle 1 ist nur sehr selten ein Leading Diagonal Triangle (LDT).
            3. Die Welle 2 ist sehr oft steil und wird durch ein Zigzag, Double- oder Triple-Zigzag ausgebildet.
            4. Die Korrekturwellen 2 und 4 sollten die entsprechenden Impulswellen zu mindestens 23,6 % korrigieren.
            5. Häufig korrigiert die Welle 2 die Welle 1 etwa zu 38,2 %, 50,0 % oder 61,8 %.
            6. Die Welle 3 dehnt sich häufig zu 161,8 % oder 261,8 % aus.
            7. In Aktienmärkten dehnt sich sehr häufig die Welle 3 aus. Bei den Rohstoffen (Commodities) ist eine Ausdehnung in der Welle 5 wahrscheinlicher.
            8. Die Welle 4 ist sehr selten ein Zigzag.
            9. Die Welle 4 korrigiert die Welle 3 oft zu 38,2 %.
            10. Ein Wellenschnitt der Wellen 1 und 4 kommt nur in Ausnahmefällen vor (LDT, EDT).
            11. Die Korrekturen der Wellen 2 und 4 wechseln meist zwischen steil und flach.
            12. Die Welle 2 korrigiert sehr oft bis in den Bereich der vorherigen Welle 4 (einen Wellengrad tiefer). Zu 80 % wird sogar das Ende der Welle 4 erreicht.
            13. Eine ausgedehnte Welle 5 erreicht sehr häufig das 1,618 fache vom Anfang der Welle 1 bis zum Ende der Welle 3.
            14. Entwickelt sich eine ausgedehnte Welle 3, sind die Wellen 1 und 5 normalerweise preislich und zeitlich etwa gleich lang.
            15. Eine Welle 5 weist weniger Volumen auf als die Welle 3.
            16. Die Welle 5 erreicht sehr häufig 61,8 %, 100 % oder 161,8 % der Welle 1.

        Rules and Guidelines for wave extensions:
            1. Eine extendierende Welle besteht aus 5,9,13 oder 17 Unterwellen und wirkt sich kraftvoll aus.
            2. Die Welle 2 darf nicht den Ursprungspunkt der Welle 1 schneiden. Sie ist also immer kürzer als die Welle 1.
            3. Die Welle 3 ist niemals die kürzeste Welle.
            4. Die Welle 4 darf den Kurskorridor der Welle 1 nicht schneiden.
            5. Die Welle 5 überschreitet das Ende der Welle 3 (ausgenommen versagende ‚Failure‘ 5) 

        Eine Impulswelle mit einer Ausdehnung besteht mindestens aus 9 Wellen, kann
        sich aber bis zu 13 und 17 Wellen ausweiten.
        Die 9-wellige, interne Struktur besteht also aus 5-3-5-3-5-3-5-3-5.

        Extensionen bilden sich in den Wellen 1, 3,5 sowie in den Wellen a und c. 
        """
        
        _result = []
        _temp = 0
        _offset = 0.2        
        _wave1_t = data_input[0][0]
        _wave2_t = data_input[0][1]
        _wave3_t = data_input[0][2]
        _wave4_t = data_input[0][3]
        _wave5_t = data_input[0][4]        
        _wave1_p = data_input[1][0]
        _wave2_p = data_input[1][1]
        _wave3_p = data_input[1][2]
        _wave4_p = data_input[1][3]
        _wave5_p = data_input[1][4]

        _result.append(check_lower(_wave2_p, _wave1_p))                     # Rule 4
        
        # if wave3 > wave1 than it's done, else check if wave3 > wave5 and take that result
        _temp = check_higher(_wave3_p, _wave1_p)                            # Rule 6
        if _temp:                                                           
            _result.append(_temp)
        else:
            _result.append(check_higher(_wave3_p, _wave5_p))
            
        _result.append(check_higher(_wave3_p, _wave2_p))                    # Rule 7

        _temp = _wave1_p - _wave2_p +_wave3_p - _wave4_p                    # Rule 9
        _result.append(check_out_range(_temp, 0, _wave1_p*(1 - _offset)))
        
        _result.append(check_higher((_wave5_p / _wave4_p), 0.7))            # Rule 11

        #print('_result:', _result)
        _temp = [item for item in _result if item]

        # Only if all conditons are True the pattern is valid
        if len(_temp) == len(_result):
            return True, [str("impulse")]
        else:
            return False, []

        
################################       
################################
################################



############
if __name__ == "__main__":
    datensammlung = EW_testtool_V01.Database()
    simple_lines = EW_testtool_V01.Test(datensammlung.stock_data)
    detail_view_lines = simple_lines.detail_view_lines

    abc_correction = ABC_Correction()
    _testobject = [ [[1, 2, 1], [228.17016599999988, 6.6901849999999286, 155.97998000000007]],      #   zigzag
                    [[2, 2, 2], [300.429932, 179.40991200000008, 246.72998000000007]],              #   zigzag, flat
                    [[2, 1, 2], [71.71997099999999, 178.51000999999997, 131.30004899999994]],       #   r_flat
                    [[1, 2, 2], [117.86010799999985, 176.57006899999988, 233.67016599999988]],      #   e_flat
                  ]

    for item in _testobject:
        _result = abc_correction.check(item)
        for element in _result:
            print(element) 

    impulse = Impulse()
    _testobject = [ [[1, 2, 3, 4, 5], [100, 33, 170, 44, 102]],
                  ]
    
    for item in _testobject:
        _result = impulse.check(item)
        for element in _result:
            print(element)
