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
import EW_types_V01


"""
Für qqqq.csv sollen folgende EW erkannt werden:

==>>> Impulse 1-2-3-4-5 aufwärts und Korrektur W-X-Y-X2-Z (W-X-Y, A-B-C) abwärts

Herangehensweise:

1.) Finde die Wellen 1-2-3-4-5 und bilde daraus einen Impuls. 
    1.1) Ein Impuls kann unterwellig sowohl Impuls 1-2-3-4-5 als auch A-B-C aufweisen
    1.2) Zu prüfen sind sowohl Extremwerte als auch Fibo-Targets und Time-Ratios
    1.3) Bei der Korrektur kann man auch gleich auf üB bzw. C-Welle testen und falls positiv,
         ein weiteres Szenario hinzufügen und den Endpunkt entsprechend korrigieren.
    1.4) 

2.) Nach dem Impuls muss eine Korrektur folgen:
    2.1) Suche die einzelnen Extrempunkte und bilde ein ABC/WXY/etc.
    2.2) Zu prüfen sind sowohl Extremwerte als auch Fibo-Targets und Time-Ratios    
    2.3) Bei der Korrektur kann man auch gleich auf üB bzw. C-Welle testen und falls positiv,
         ein weiteres Szenario hinzufügen und den Endpunkt entsprechend korrigieren.
    2.4) Eine Korrektur kann beliebig komplex werden und daher können
         mehrere Sub-Wellen entstehen bzw. zusammengefasst werden
    2.5) Wenn der Extrempunkt der Korrektur gefunden ist und nicht so recht zum Impuls passt (Fibo-Target),
         prüfe Alternativ-Szenarien die eine höhere Wahrscheinlichkeit aufweisen. (Stichwort üB, WXY, WXYX2Z)

3.) Speichere die Wellen und Sub-Wellen als Liste ab samt Wahrscheinlichkeiten, Clusterzonen, Häufigkeit & Treffergenauigkeit
    3.1) Gebe jedes mögliches Szenario in einem Diagramm aus samt Bezeichnung der jeweiligen Wellen und Berechnungen in einem
         Bild aus (Fibo-Targets, Time-Ratios, Was wurde hergenommen um es zu berechnen)
    3.2) Zeige was nicht so gut gepasst hat und wie groß die Abweichnung in Punkten und % war

4.) Zeige die Zukunft
    4.1) Berechne mögliche zukünftige Verläufe unter Berücksichtigung von den EW Regeln und vergeangenen Wellen
    4.2) Zeige Wahrscheinlichkeiten, Clusterzonen, Häufigkeit & Treffergenauigkeit
    4.3) Berechne alle möglichen Verläufe und speichere diese in einer Liste ab
    4.4) Gemeinsame Wellen sollen gut sichtbar markiert werden samt Target Zones


####################
Welle1: ==>  0 - 46 Impuls 1-2-3-4-5 oder W-X-Y (double zigzag)
1.) Starte am Minimum und gehe solange weiter hoch, bis kein weiteres Maximum mehr erreicht werden kann
    Welle 3 = 1
    Welle 5 == 3,1

Welle2: ==> 46 - 75 (W-X-Y-X2-Z)
1.) Starte am Ende Welle 1 und suche das darauffolgende Minimum (53)
2.) Korrekturen können alle möglichen Variaten sein, daher kann es 1,3,5,7,9,ect. Koorektur-Wellen geben
    Man muss jetzt prüfen und die nächsten Wellen 2(up) und 3(down) zum Korrekturmuster passen oder schön zum nächsten Impuls
    Fibo_targets und Time-Ratio sollten ausreichen.
    Ebenso sollte man auf üB oder bereits C-Welle ind er Korrektur prüfen und so das Maximum von Welle korrigieren und diese Welle
    in einem zweiten Szenario abspeichern.
3.) Die Wellen W-X-Y-X2-Z als Welle 2 abspeichern und evtl. gleich die Subwellen bestimmen
    W = 76.4% retracement von Welle 1
    X == W, Y ==X,W
    X2 == 76.4%*X
    Z == W

Welle3: ==>  75 - 165
1.) Vorgehensweise siehe Welle 1
2.) Welle 3 ist ein 1-2-3-4-5 Impuls.

Welle 3 kann auch als A-B-C angesehen werden. c = 127.2%*a.


Welle4: ==> (1) 165 - 170 oder (2) 165 - 175
1.) siehe Welle 2.
Fall (1): Es ist möglich , dass es nur ein einfaches A-B-C ist mit C = 200%*B oder auch
          als A-B-C Korrektur von dem A-B-C (1-2-3) angesehen werden. welle 4 retracement 76.4% vom A-B-C (1-2-3).
Fall (2): oder aber eine Fail c hat die nur 76.4% von B beträgt (2)


Welle5: ==>   Entweder 1-2-3-4-5 oder auch A-B-C
Hier kann es 2 verschidene Endpunkte geben.
1-2-3-4-5 mit einer sehr kurzen 1 und etwa 3 == 5.
A-B-C mit A == C
####################

Impuls Variante 1: Welle 4 mit failed c Welle und Welle 5 mit hohem Maximum:
Welle 2 == retrace bis 76.4%*, komplexes Muster
Welle 3 == 127.2%*1
Welle 4 == retrace bis 61.8%, einfaches Muster
Welle 5 == 138.2%*1

Impuls Variante 2: Welle 4 als simples A-B-C und Welle 5 mit niedrigem Maximum:
Welle 2 == retrace bis 76.4%*, komplexes Muster
Welle 3 == 127.2%*1
Welle 4 == retrace bis 61.8%, einfaches Muster
Welle 5 == 138.2%*1

Impuls Variante 3: Welle 4 mit failed c Welle und Welle 5 mit hohem Maximum:
Welle 2 == retrace bis 76.4%*, komplexes Muster
Welle 3 == 127.2%*1
Welle 4 == retrace bis 61.8%, einfaches Muster
Welle 5 weit größer als 138.2%*1 und findet kein wirkliches Fibo-Target

Korrektur W-X-Y oder W-X-Y-X2-Z:
Retracement bis 23.6% vom Impuls
"""


def ratio_hi_lo(value_1, value_2, *debug_flag):
    """
    checks wich value is higher and creates the ratio between
    higher value / lower_value and returns True/False for value_1 or value_2 and the ratio
    returned values: value_1>, value_2>, ratio(hi/lo)
    """
    if debug_flag[0]:
        print("======== ratio_hi_lo(value_1, value_2, *debug_flag): ========")
    if value_1 > value_2:
        if debug_flag[0]:
            print("value_1 > value_2:", True, False, value_1 / value_2)
        return True, False, value_1 / value_2
    else:
        if debug_flag[0]:
            print("value_2 > value_1:", False, True, value_2 / value_1)        
        return False, True, value_2 / value_1


def direction_flag(value_1, value_2, *debug_flag):
    """
    create a direction flag str("up") or str("down").
    """
    _direction = 0
    
    if value_2 > value_1:
        _direction = str("up")
    else:
        _direction = str("down")
        
    return _direction

def list_unpack(list_input, position, *debug_flag):
    """
    """
    if debug_flag:
        print('======== list_unpack ========')
    a = list_input[position]
    if debug_flag:
        print(a)
    if a and type(a) == list:
        b = a[position]
        if debug_flag:
            print(a)
        if b and type(b) == list:
            c = b[position]
            if debug_flag:
                print(c)
            if c and type(c) == list:
                print("list could not be unpacked! ")
            else:
                return c
        else:
            return b
    else:
        return a


################################       
################################
################################
class TEST():
    """
    parse the database and try to find valid EW vertexes inside

    ====>>>> Mssing: Step0: Find the start point (Extremum Min or Max) for the following operations
    
    Step1: Combine always the following 3 lines to a zigzag and save it.
    Step2: Send this zigzag to the analyzer modul
    Step3: After the 2nd zigzag is finished we can try to combine the first 2 to new pattern.
            Step3.1: Send the new combined waves to the analyzer modul
    Step4: After the 3rd zigzag is finished we can try to combine the first comb_lvl_1 with a new basis_wave
            Step4.1: Send the new combined waves to the analyzer modul

    """
    def __init__(self, data_input):
        """
        data_input = {}   # ["_line_id" : "spare", "direction", [X], [Y]]

        self.basis_waves = {} ==> The following 3 lines on the lowest level 
        self.comb_lvl_1 = {} ==> Combines 2 basis_waves to one with a higher degree.
        
        """
        self.database = data_input

##        print("#########################################   self.database   #####################################################")
##        print("{0:>5} {1:<45} {2:<10} {3:<20} {4:<20}".format('Index', 'spare', 'Direction', '[X]','[Y]'))
##        for item in self.database:
##            print("{0:>5} {1:<45} {2:<10} {3:<20} {4:<20}".format(item, self.database[item][0], self.database[item][1],self.database[item][2],self.database[item][3]))
##        print("########################################################################################################################")

        
        self.basis_waves = {}
        self.basis_waves_results = {}
        
        self.comb_lvl_1 = {}
        self.comb_lvl_1_results = {}

        self.comb_lvl_2 = {}
        self.comb_lvl_2_results = {}        
        
        self.analyzer = EW_types_V01.Analyzer()


        debug_flag = False

        self.parse_database(debug_flag)




            


    def parse_database(self, debug_flag):
        """
        self.basis_waves = {}         # { "_line_id" : ["abc", "a_line - b_line - c_line", [X], [Y], [time_values], [price_values]] }
        self.basis_waves_results = {} # [ "_line_id" : [result b_a], [result c_b], [result c_a], valid True/False, [pattern type] }
        
                         results = [] # [ {"wave2_wave1" : result, best_fit_fibratio_n, discrepancy, best_fit_fibratio_e, discrepancy},
                                          {"wave3_wave2" : result, best_fit_fibratio_n, discrepancy, best_fit_fibratio_e, discrepancy},
                                          {"wave3_wave1" : result, best_fit_fibratio_n, discrepancy, best_fit_fibratio_e, discrepancy},
                                        ]
        """
        
        _line_id = 0
        _line_in_progress = False
        _counter = 0


        #Step1: Combine always the following 3 lines to a zigzag and save it.
        for item in self.database:
            
            if _counter == 3:
                _counter -= 3
                
            _counter += 1

            # The first item creates a new entry in the lvl_1_waves dict.
            if item == 1:
                _line_id += 1
                _line_in_progress = True                
                self.basis_waves[_line_id] = [ str("a"),
                                               [item],
                                               self.database[item][2],
                                               self.database[item][3],
                                               [ abs(self.database[item][2][-1] - self.database[item][2][0]) +1 ], # +1 damit man keine 0 im time_value hat
                                               [ abs(self.database[item][3][-1] - self.database[item][3][0]) ],
                                             ]
                #print(item, _line_id, self.basis_waves[_line_id])

            if item != 1:
                # Create a new entry in the lvl_1_waves dict.
                if not _line_in_progress:
                    _line_id += 1
                    _line_in_progress = True                
                    self.basis_waves[_line_id] = [ str("a"),
                                                   [item],
                                                   self.database[item][2],
                                                   self.database[item][3],
                                                   [ abs(self.database[item][2][-1] - self.database[item][2][0]) +1 ], # +1 damit man keine 0 im time_value hat
                                                   [ abs(self.database[item][3][-1] - self.database[item][3][0]) ],
                                                 ]
                    #print(item, _line_id, self.basis_waves[_line_id])
                
                # Add the b-wave
                if _line_in_progress and _counter == 2:
                    self.basis_waves[_line_id][0] += (str("b")) 
                    self.basis_waves[_line_id][1].append(item)                                                  
                    self.basis_waves[_line_id][2].append(self.database[item][2][-1])
                    self.basis_waves[_line_id][3].append(self.database[item][3][-1])
                    self.basis_waves[_line_id][4].append(abs(self.database[item][2][-1] - self.basis_waves[_line_id][2][1]) +1) # +1 damit man keine 0 im time_value hat
                    self.basis_waves[_line_id][5].append(abs(self.database[item][3][-1] - self.basis_waves[_line_id][3][1]))
                    #print(item, _line_id, self.basis_waves[_line_id])

                # Add the c-wave and reset _line_in_progress flag              
                if _line_in_progress and _counter == 3:
                    self.basis_waves[_line_id][0] += (str("c")) 
                    self.basis_waves[_line_id][1].append(item)                                                  
                    self.basis_waves[_line_id][2].append(self.database[item][2][-1])
                    self.basis_waves[_line_id][3].append(self.database[item][3][-1])
                    self.basis_waves[_line_id][4].append(abs(self.database[item][2][-1] - self.basis_waves[_line_id][2][2]) +1) # +1 damit man keine 0 im time_value hat
                    self.basis_waves[_line_id][5].append(abs(self.database[item][3][-1] - self.basis_waves[_line_id][3][2]))                    
                    _line_in_progress = False
                    #print(item, _line_id, self.basis_waves[_line_id])

                    #Step2: Send this zigzag to the analyzer modul and receive the result
                    self.basis_waves_results[_line_id] = self.analyzer.analyze(self.basis_waves[_line_id], debug_flag)


                #Step3: After the 2nd zigzag is finished we can try to combine the first 2 basis_waves to a new one ===> comb_lvl_1.
                # This new wave can be either an abc or impulse pattern
                if _line_id == 2 and not _line_in_progress:
                    self.comb_lvl_1, self.comb_lvl_1_results = self.combine_basis_waves(self.basis_waves[_line_id-1], self.basis_waves[_line_id], debug_flag)


                #Step4: After the 3rd zigzag is finished we can try to combine the first comb_lvl_1 with a new basis_wave
                if _line_id == 3 and not _line_in_progress:
                    self.comb_lvl_2, self.comb_lvl_2_results = self.combine_basis_waves(self.comb_lvl_1[1], self.basis_waves[_line_id], debug_flag)



        print("###############################################   self.basis_waves   ##########################################################")
        print("{0:>7} {1:<7} {2:<16} {3:<20} {4:<52} {5:<12} {6:<20}".format('[Index]', '[count]', '[included waves]', '[X]','[Y]', '[t_values]', '[p_values]'))
        for item in self.basis_waves:
            print("{0:>7} {1:<7} {2:<16} {3:<20} {4:<52} {5:<12} {6:<20}".format(item, self.basis_waves[item][0], self.basis_waves[item][1],
                                                                                 self.basis_waves[item][2],self.basis_waves[item][3],
                                                                                 self.basis_waves[item][4],self.basis_waves[item][5]))
            try:
                for element in self.basis_waves_results[item][0]:
                    print("        {0:<60}".format(element))
            except:
                pass
        print("##############################################################################################################################")

        print("############################################   self.comb_lvl_1_waves   #######################################################")
        print("{0:>7} {1:<7} {2:<20} {3:<20} {4:<52} {5:<12} {6:<20}".format('[Index]', '[count]', '[included waves]', '[X]','[Y]', '[t_values]', '[p_values]'))
        for item in self.comb_lvl_1:
            print("{0:>7} {1:<7} {2:<20} {3:<20} {4:<52} {5:<12} {6:<20}".format(item, self.comb_lvl_1[item][0], self.comb_lvl_1[item][1],
                                                                                 self.comb_lvl_1[item][2],self.comb_lvl_1[item][3],
                                                                                 self.comb_lvl_1[item][4],self.comb_lvl_1[item][5]))
            try:
                for element in self.comb_lvl_1_results[item]:
                    print("        {0:<60}".format(element))
            except:
                pass
        print("##############################################################################################################################")

        print("############################################   self.comb_lvl_2_waves   #######################################################")
        print("{0:>7} {1:<7} {2:<20} {3:<20} {4:<52} {5:<12} {6:<20}".format('[Index]', '[count]', '[included waves]', '[X]','[Y]', '[t_values]', '[p_values]'))
        for item in self.comb_lvl_2:
            print("{0:>7} {1:<7} {2:<20} {3:<20} {4:<52} {5:<12} {6:<20}".format(item, self.comb_lvl_2[item][0], self.comb_lvl_2[item][1],
                                                                                 self.comb_lvl_2[item][2],self.comb_lvl_2[item][3],
                                                                                 self.comb_lvl_2[item][4],self.comb_lvl_2[item][5]))
            try:
                for element in self.comb_lvl_2_results[item]:
                    print("        {0:<60}".format(element))
            except:
                pass
        print("##############################################################################################################################")

    
            
    def combine_basis_waves(self, wave_1, wave_2, debug_flag):
        """
        basis_wave:                                    ["abc", "a_line - b_line - c_line", [X], [Y], [time_values], [price_values]]
        self.comb_lvl_1 = {}          # { "_line_id" : ["abc", "a_line - b_line - c_line", [X], [Y], [time_values], [price_values]] }
        self.comb_lvl_1_results = {}  #
        _missing_r_wave = []          #                ["m_r_wave", "_line",               [X], [Y], [time_values], [price_values]] 
        

        Case1: up direction of a_wave in wave_1 

	    Case1.1: down direction of a_wave in wave_2. ==> different direction ==> no missing retracement wave exists

            	Step1: If max(wave2) > max(wave1) we can combine it

	    	Step2: Find the dominant retracement wave (b_wave in wave_1 or a_wave in wave_2) and create a new abc pattern
                       If both corrective waves are almost equal, we have to create 2 new waves

            	Step3: Create an impulse ending at b_wave of wave_2.


	    Case1.2: up direction of a_wave in wave_2. ==> Both waves with same direction ==> missing retracement wave exists

            	Step1: If max(a_wave of wave2) > max(wave1) we can combine it

	    	Step2: Find the dominant retracement wave (b_wave in wave_1 or the missing rectracement basis_wave) 
			 and create a new abc pattern ending at a_wave of wave_2.
                         If both corrective waves are almost equal, we have to create 2 new waves

	    	Step3: Create an impulse with the missing rectracement basis_wave ending at a_wave of wave_2.



            	Step4: If max(c_wave of wave2) > max(a_wave of wave2) we can combine it. 

	    	Step5: Find the dominant retracement wave (b_wave in previous combined_wave or b_wave in wave_2)
		       and create a new abc pattern ending at c_wave of wave_2.
                       If both corrective waves are almost equal, we have to create 2 new waves

	    	Step6: Create 3 new impulses using the one before and modify it. All impulses end at c_wave of wave_2.
		       3 because we have 1 new point and need to modify always 1 wave. (long_wave1, long_wave3, long_wave5)


        Case2: down direction of a_wave in wave_1

            Step1: see above .......
	    ...........

        Last_Step: Only valid patterns can be accepted and returned.
                   Check all results and only keep valid patterns and add them to the output_data

        """
        
        combined_waves = {}
        combined_waves_results = {}
        
        output_data = {}
        output_data_results = {}
        
        _direction_wave1 = 0
        _direction_wave2 = 0
        _dom_wave1 = 0
        _dom_wave2 = 0
        _ratio = 0
        _trigger = 1.30
        _line_id = 0
        _line_in_progress = False
        _missing_r_wave = []
        _temp = 0

        if debug_flag:
            print("#############     combine_basis_waves(self, wave_1, wave_2, debug_flag):     #############")

        # create direction flags for further calculation purposes
        _direction_wave1 = direction_flag(wave_1[3][0], wave_1[3][1])
        _direction_wave2 = direction_flag(wave_2[3][0], wave_2[3][1])
        
        if debug_flag:
            print("_direction_wave1:", _direction_wave1, "_direction_wave2:", _direction_wave2)

        # Case 1: up direction of a_wave in wave_1
        if _direction_wave1 == "up":

            # Case1.1: down direction of a_wave in wave_2. ==> different direction ==> no missing retracement wave exists
            if _direction_wave2 == "down":

                if debug_flag:
                    print("Case1.1: if _direction_wave1 == 'up' if _direction_wave2 == 'down':") 

                # Step1: If max(wave2) > max(wave1) we can combine it
                if debug_flag:
                    print("Step1: max(wave_2[3]) > max(wave_1[3]):", max(wave_2[3]),  max(wave_1[3]))               
                if max(wave_2[3]) > max(wave_1[3]):

                    # Step2: Find the dominant retracement wave (b_wave in wave_1 or a_wave in wave_2) and create a new abc pattern
                    #        If both corrective waves are almost equal, we have to create 2 new waves
                    _dom_wave1, _dom_wave2, _ratio = ratio_hi_lo(wave_1[5][1], wave_2[5][0], debug_flag)

                    # Also include time values to decide which one is the dominant retracement wave !!!
                    if _dom_wave1 and _ratio >= _trigger and wave_1[4][1] >= wave_2[4][0]:

                        if debug_flag:
                            print("Step2: if _dom_wave1 and _ratio >= _trigger and wave_1[4][1] >= wave_2[4][0]:")
                    
                        _line_id += 1
                        #_line_in_progress = True                
                        combined_waves[_line_id] = [ str("abc"),
                                                    [ wave_1[1][0], wave_1[1][1], [wave_1[1][2], wave_2[1][0], wave_2[1][1]] ],
                                                    [ wave_1[2][0], wave_1[2][1], wave_1[2][2], wave_2[2][2] ],
                                                    [ wave_1[3][0], wave_1[3][1], wave_1[3][2], wave_2[3][2] ],
                                                    [ wave_1[4][0], wave_1[4][1], abs(wave_2[2][2] - wave_1[2][2]) +1 ],  # +1 damit man keine 0 im time_value hat
                                                    [ wave_1[5][0], wave_1[5][1], abs(wave_2[3][2] - wave_1[3][2]) ],
                                                   ]
                        # Send these combined waves to the analyzer modul and receive the result
                        combined_waves_results[_line_id] = self.analyzer.analyze(combined_waves[_line_id], debug_flag)


                    elif _dom_wave2 and _ratio >= _trigger and wave_2[4][0] >= wave_1[4][1]:

                        if debug_flag:
                            print("Step2: elif _dom_wave2 and _ratio >= _trigger and wave_2[4][0] >= wave_1[4][1]:")
                            
                        _line_id += 1
                        #_line_in_progress = True                
                        combined_waves[_line_id] = [ str("abc"),
                                                    [wave_1[1], wave_2[1][0], wave_2[1][1] ],
                                                    [wave_1[2][0], wave_1[2][-1], wave_2[2][1], wave_2[2][2] ],
                                                    [wave_1[3][0], wave_1[3][-1], wave_2[3][1], wave_2[3][2] ],
                                                    [abs(wave_1[2][-1] - wave_1[2][0]) +1, wave_2[4][0], wave_2[4][1] ],  # +1 damit man keine 0 im time_value hat
                                                    [abs(wave_1[3][-1] - wave_1[3][0]), wave_2[5][0], wave_2[5][1] ],
                                                   ]
                        # Send these combined waves to the analyzer modul and receive the result
                        combined_waves_results[_line_id] = self.analyzer.analyze(combined_waves[_line_id], debug_flag)


                    # else: If both corrective waves are almost equal, we have to create 2 new waves
                    else:
                        print("Step2: This part need to be programmed first!")
                        pass
                        

                    # Step3: Create an 12345 (IMPULSE/LDT/EDT) ending at b_wave of wave_2.
                    if debug_flag:
                        print("Step3: Create an 12345 (IMPULSE/LDT/EDT) ending at b_wave of wave_2.")
                    
                    _line_id += 1
                    #_line_in_progress = True                
                    combined_waves[_line_id] = [ str("12345"),
                                                [wave_1[1][0], wave_1[1][1], wave_1[1][2], wave_2[1][0], wave_2[1][1] ],
                                                [wave_1[2][0], wave_1[2][1], wave_1[2][2], wave_1[2][3], wave_2[2][1], wave_2[2][2] ],
                                                [wave_1[3][0], wave_1[3][1], wave_1[3][2], wave_1[3][3], wave_2[3][1], wave_2[3][2] ],
                                                [wave_1[4][0], wave_1[4][1], wave_1[4][2], wave_2[4][0], wave_2[4][1] ],
                                                [wave_1[5][0], wave_1[5][1], wave_1[5][2], wave_2[5][0], wave_2[5][1] ],
                                               ]
                    # Send these combined waves to the analyzer modul and receive the result IMPULSE/LDT/EDT             
                    combined_waves_results[_line_id] = self.analyzer.analyze(combined_waves[_line_id], debug_flag)


            # Case1.2: up direction of a_wave in wave_2. ==> Both waves with same direction ==> missing retracement wave exists
            if _direction_wave2 == "up":

                if debug_flag:
                    print("Case1.2: if _direction_wave1 == 'up' if _direction_wave2 == 'up':") 
                
                # Step1: If max(a_wave of wave2) > max(wave1) we can combine it
                if debug_flag:
                    print("Step1: max(wave_2[3][0:2]) > max(wave_1[3]):", max(wave_2[3][0:2]),  max(wave_1[3]))
                    
                if max(wave_2[3][0:2]) > max(wave_1[3]):

                    
                    # Step2.1: Get the missing retracement wave. This is the end of wave_1 and the beginning of wave_2
                    _missing_r_wave = [ str("m_r_wave"),
                                        [ list_unpack(wave_1[1], -1)+1],
                                        [ wave_1[2][-1], wave_2[2][0]],
                                        [ wave_1[3][-1], wave_2[3][0]],
                                        [ abs(wave_2[2][0] - wave_1[2][-1]) +1 ],  # +1 damit man keine 0 im time_value hat
                                        [ abs(wave_2[3][0] - wave_1[3][-1])],
                                      ]
                    if debug_flag:
                        print("_missing_r_wave:", _missing_r_wave)

                    # Step2.2: Find the dominant retracement wave (b_wave in wave_1 or the missing rectracement basis_wave) 
                    #	 and create a new abc pattern ending at A of wave_2.
                    #        If both corrective waves are almost equal, we have to create 2 new waves                    
                    _dom_wave1, _dom_wave2, _ratio = ratio_hi_lo(wave_1[5][1], _missing_r_wave[5][0], debug_flag)

                    
                    # Also include time values to decide which one is the dominant retracement wave !!!
                    if _dom_wave1 and _ratio >= _trigger and wave_1[4][1] >= _missing_r_wave[4][0]:

                        if debug_flag:
                            print("Step2.2: if _dom_wave1 and _ratio >= _trigger and wave_1[4][1] >= _missing_r_wave[4][0]:") 
                        
                        _line_id += 1
                        #_line_in_progress = True                
                        combined_waves[_line_id] = [ str("abc"),
                                                    [wave_1[1][0], wave_1[1][1], [wave_1[1][2], _missing_r_wave[1][0], wave_2[1][0]] ],
                                                    [wave_1[2][0], wave_1[2][1], wave_1[2][2], wave_2[2][1] ],
                                                    [wave_1[3][0], wave_1[3][1], wave_1[3][2], wave_2[3][1] ],
                                                    [wave_1[4][0], wave_1[4][1], abs(wave_2[2][1] - wave_1[2][2]) +1 ],  # +1 damit man keine 0 im time_value hat
                                                    [wave_1[5][0], wave_1[5][1], abs(wave_2[3][1] - wave_1[3][2]) ],
                                                   ]
                        # Send these combined waves to the analyzer modul and receive the result
                        combined_waves_results[_line_id] = self.analyzer.analyze(combined_waves[_line_id], debug_flag)

                    
                    elif _dom_wave2 and _ratio >= _trigger and _missing_r_wave[4][0] >= wave_1[4][1]:
                        _line_id += 1

                        if debug_flag:
                            print("Step2.2: elif _dom_wave2 and _ratio >= _trigger and _missing_r_wave[4][0] >= wave_1[4][1]:")
                            
                        #_line_in_progress = True                
                        comb_lvl_1[_line_id] = [ str("abc"),
                                                [wave_1[1], _missing_r_wave[1][0], wave_2[1][0] ],
                                                [wave_1[2][0], wave_1[2][-1], wave_2[2][0], wave_2[2][1] ],
                                                [wave_1[3][0], wave_1[3][-1], wave_2[3][0], wave_2[3][1] ],
                                                [abs(wave_1[2][-1] - wave_1[2][0]) +1, _missing_r_wave[4][0], wave_2[4][0] ],  # +1 damit man keine 0 im time_value hat
                                                [abs(wave_1[3][-1] - wave_1[3][0]), _missing_r_wave[5][0], wave_2[5][0] ],
                                               ]
                        # Send these combined waves to the analyzer modul and receive the result
                        combined_waves_results[_line_id] = self.analyzer.analyze(combined_waves[_line_id], debug_flag)


                    # else: If both corrective waves are almost equal, we have to create 2 new waves
                    else:
                        print("Step2.2: This part need to be programmed first!")
                        pass
                    

                    # Step3: Create an 12345 (IMPULSE/LDT/EDT) with the missing rectracement basis_wave ending at A of wave_2.
                    if debug_flag:
                        print("Step3: Create an 12345 (IMPULSE/LDT/EDT) with the missing rectracement basis_wave ending at A of wave_2.")
                        
                    _line_id += 1
                    #_line_in_progress = True                
                    combined_waves[_line_id] = [ str("12345"),
                                                [wave_1[1][0], wave_1[1][1], wave_1[1][2], _missing_r_wave[1][0], wave_2[1][0] ],
                                                [wave_1[2][0], wave_1[2][1], wave_1[2][2], wave_1[2][3], wave_2[2][0], wave_2[2][1] ],
                                                [wave_1[3][0], wave_1[3][1], wave_1[3][2], wave_1[3][3], wave_2[3][0], wave_2[3][1] ],
                                                [wave_1[4][0], wave_1[4][1], wave_1[4][2], _missing_r_wave[4][0], wave_2[4][0] ],
                                                [wave_1[5][0], wave_1[5][1], wave_1[5][2], _missing_r_wave[5][0], wave_2[5][0] ],
                                               ]
                    # Send these combined waves to the analyzer modul and receive the result IMPULSE/LDT/EDT             
                    combined_waves_results[_line_id] = self.analyzer.analyze(combined_waves[_line_id], debug_flag)


                # Step4: If max(c_wave of wave2) > max(a_wave of wave2) we can combine it.
                if debug_flag:
                    print("Step4: max(wave_2[3][2:]) > max(wave_2[3][0:2])", max(wave_2[3][2:]), max(wave_2[3][0:2]))
                    
                if max(wave_2[3][2:]) > max(wave_2[3][0:2]):
                
                    # Step5: Find the dominant retracement wave (b_wave in previous combined abc_wave or b_wave in wave_2)
                    #        and create a new abc pattern ending at C of wave_2.
                    #        If both corrective waves are almost equal, we have to create 2 new waves
                    
                    _temp = combined_waves[_line_id-1]  # get the previous combined abc_wave
                    
                    if debug_flag:
                        print("Step5: previous combined abc_wave:")
                        print(_temp)
                        
                    _dom_wave1, _dom_wave2, _ratio = ratio_hi_lo(_temp[5][1], wave_2[5][1], debug_flag)

                    # Also include time values to decide which one is the dominant retracement wave !!!
                    if _dom_wave1 and _ratio >= _trigger and _temp[4][1] >= wave_2[4][1]:
                        
                        if debug_flag:
                            print("Step5: if _dom_wave1 and _ratio >= _trigger and _temp[4][1] >= wave_2[4][1]:")
                            
                        _line_id += 1
                        #_line_in_progress = True                
                        combined_waves[_line_id] = [ str("abc"),
                                                    [_temp[1][0], _temp[1][1], [_temp[1][2], wave_2[1][1], wave_2[1][2]] ],
                                                    [_temp[2][0], _temp[2][1], _temp[2][2], wave_2[2][3] ],
                                                    [_temp[3][0], _temp[3][1], _temp[3][2], wave_2[3][3] ],
                                                    [_temp[4][0], _temp[4][1], abs(wave_2[2][3] - _temp[2][2]) +1 ],  # +1 damit man keine 0 im time_value hat
                                                    [_temp[5][0], _temp[5][1], abs(wave_2[3][3] - _temp[3][2]) ],
                                                   ]
                        # Send these combined waves to the analyzer modul and receive the result
                        combined_waves_results[_line_id] = self.analyzer.analyze(combined_waves[_line_id], debug_flag)

                    
                    elif _dom_wave2 and _ratio >= _trigger and wave_2[4][1] >= _temp[4][1]:
                        
                        if debug_flag:
                            print("Step5: elif _dom_wave2 and _ratio >= _trigger and wave_2[4][1] >= _temp[4][1]:")
                        
                        _line_id += 1
                        #_line_in_progress = True                
                        combined_waves[_line_id] = [ str("abc"),
                                                    [_temp[1], wave_2[1][1], wave_2[1][2] ],
                                                    [_temp[2][0], _temp[2][-1], wave_2[2][2], wave_2[2][3] ],
                                                    [_temp[3][0], _temp[3][-1], wave_2[3][2], wave_2[3][3] ],
                                                    [abs(_temp[2][-1] - _temp[2][0]) +1, wave_2[4][1], wave_2[4][2] ],  # +1 damit man keine 0 im time_value hat
                                                    [abs(_temp[3][-1] - _temp[3][0]), wave_2[5][1], wave_2[5][2] ],
                                                   ]
                        # Send these combined waves to the analyzer modul and receive the result
                        combined_waves_results[_line_id] = self.analyzer.analyze(combined_waves[_line_id], debug_flag)


                    # else: If both corrective waves are almost equal, we have to create 2 new waves
                    else:
                        print("Step5: This part need to be programmed first!")
                        pass
                    

                    # Step6: Create 3 new 12345 (IMPULSE/LDT/EDT) using the one before and modify it.
                    #        All impulses ending at C of wave_2.
                    #        3 because we have 1 new extremum and need to modify always 1 wave. (long_wave1, long_wave3, long_wave5)
                    #        Before combining the waves, we need to check the dominant retracement wave
                    #        if it's possible to combine waves and create the 12345 (IMPULSE/LDT/EDT).
                    
                    _temp = combined_waves[_line_id-1]  # get the previous combined 12345_wave
                    
                    if debug_flag:
                        print("Step6: previous combined 12345_wave:")
                        print(_temp)

                    _dom_wave1, _dom_wave2, _ratio = ratio_hi_lo(_temp[5][3], _temp[5][1], debug_flag)  #compare wave4_temp against wave2_temp of the previous combined 12345_wave

                    # Also include time values to decide which one is the dominant retracement wave !!!
                    if _dom_wave1 and _ratio >= _trigger and _temp[4][3] >= _temp[4][1]:    #wave4_temp is dominant 

                        if debug_flag:
                            print("Step6: if _dom_wave1 and _ratio >= _trigger and _temp[4][3] >= _temp[4][1]: ")
                            print("12345_wave 1/3:   old(1,2,3)==>new(1) long_wave1")

                        # 12345_wave 1/3:   old(1,2,3)==>new(1) long_wave1
                        _line_id += 1                                                                       
                        #_line_in_progress = True                
                        combined_waves[_line_id] = [ str("12345"),
                                                    [[ _temp[1][0], _temp[1][1], _temp[1][2] ], _temp[1][3], _temp[1][4], wave_2[1][1], wave_2[1][2] ],
                                                    [_temp[2][0], _temp[2][3], _temp[2][4], _temp[2][5], wave_2[2][2], wave_2[2][3] ],
                                                    [_temp[3][0], _temp[3][3], _temp[3][4], _temp[3][5], wave_2[3][2], wave_2[3][3] ],
                                                    [abs(_temp[2][3] - _temp[2][0]) +1, _temp[4][3], _temp[4][4], wave_2[4][1], wave_2[4][2] ],   # +1 damit man keine 0 im time_value hat
                                                    [abs(_temp[3][3] - _temp[3][0]), _temp[5][3], _temp[5][4], wave_2[5][1], wave_2[5][2] ],
                                                   ]
                        # Send these combined waves to the analyzer modul and receive the result IMPULSE/LDT/EDT             
                        combined_waves_results[_line_id] = self.analyzer.analyze(combined_waves[_line_id], debug_flag)


                    # Also include time values to decide which one is the dominant retracement wave !!!
                    elif _dom_wave2 and _ratio >= _trigger and _temp[4][1] >= _temp[4][3]:  #wave2_temp is dominant 

                        if debug_flag:
                            print("Step6: elif _dom_wave2 and _ratio >= _trigger and _temp[4][1] >= _temp[4][3]:")

                        _dom_wave1, _dom_wave2, _ratio = ratio_hi_lo(wave_2[5][1], _temp[5][3], debug_flag) #compare b_wave2 against wave4_temp of the previous combined 12345_wave

                        if _dom_wave1 and _ratio >= _trigger and wave_2[4][1] >= _temp[4][3]:    #wave2_temp and b_wave2 are dominant 

                            if debug_flag:
                                print("Step6: if _dom_wave1 and _ratio >= _trigger and wave_2[4][1] >= _temp[4][3]:")
                                print("12345_wave 2/3:   old(3,4,5)==>new(3) long_wave3")

                            # 12345_wave 2/3:   old(3,4,5)==>new(3) long_wave3
                            _line_id += 1                                                                       
                            #_line_in_progress = True                
                            combined_waves[_line_id] = [ str("12345"),
                                                        [_temp[1][0], _temp[1][1], [ _temp[1][2], _temp[1][3], _temp[1][4] ], wave_2[1][1], wave_2[1][2] ],
                                                        [_temp[2][0], _temp[2][1], _temp[2][2], _temp[2][-1], wave_2[2][2], wave_2[2][3] ],
                                                        [_temp[3][0], _temp[3][1], _temp[3][2], _temp[3][-1], wave_2[3][2], wave_2[3][3] ],
                                                        [_temp[4][0], _temp[4][1], abs(_temp[2][-1] - _temp[2][2]) +1, wave_2[4][1], wave_2[4][2] ],   # +1 damit man keine 0 im time_value hat
                                                        [_temp[5][0], _temp[5][1], abs(_temp[3][-1] - _temp[3][2]), wave_2[5][1], wave_2[5][2] ],
                                                       ]
                            # Send these combined waves to the analyzer modul and receive the result IMPULSE/LDT/EDT             
                            combined_waves_results[_line_id] = self.analyzer.analyze(combined_waves[_line_id], debug_flag)

                        elif _dom_wave2 and _ratio >= _trigger and _temp[4][3] >= wave_2[4][1]:    #wave2_temp and wave4_temp is dominant

                            if debug_flag:
                                print("Step6: elif _dom_wave2 and _ratio >= _trigger and _temp[4][3] >= wave_2[4][1]:")
                                print("12345_wave 3/3:   old(5,b_wave2,c_wave2)==>new(5) long_wave5")

                            # 12345_wave 3/3:   old(5,b_wave2,c_wave2)==>new(5) long_wave5
                            _line_id += 1                                                                       
                            #_line_in_progress = True                
                            combined_waves[_line_id] = [ str("12345"),
                                                        [_temp[1][0], _temp[1][1], _temp[1][2], _temp[1][3], [ _temp[1][4], wave_2[1][1], wave_2[1][2] ] ],
                                                        [temp[2][0], _temp[2][1], _temp[2][2], _temp[2][3], _temp[2][4], wave_2[2][3] ],
                                                        [temp[3][0], _temp[3][1], _temp[3][2], _temp[3][3], _temp[3][4], wave_2[3][3] ],
                                                        [_temp[4][0], _temp[4][1], _temp[4][2], _temp[4][3], abs(wave_2[2][-1] - _temp[2][4]) +1 ],   # +1 damit man keine 0 im time_value hat
                                                        [_temp[5][0], _temp[5][1], _temp[5][2], _temp[5][3], abs(wave_2[3][-1] - _temp[3][4]) ],
                                                       ]
                            # Send these combined waves to the analyzer modul and receive the result IMPULSE/LDT/EDT             
                            combined_waves_results[_line_id] = self.analyzer.analyze(combined_waves[_line_id], debug_flag)


                        # else: If both corrective waves are almost equal, we have to create 2 new waves
                        else:
                            print("Step6: This part need to be programmed first!")
                            pass




        # Case 2: down direction of a_wave in wave_1
        if _direction_wave1 == "down":
            pass    






        # Last Step: Only valid patterns can be accepted and returned.
        # Check all results and only keep valid patterns and add them to the output_data
        for item in combined_waves_results:
            _temp = []

            if len(combined_waves_results[item]) > 1:
                for element in combined_waves_results[item]:
                    if debug_flag:
                        print("______ len(combined_waves_results[item]) > 1:")
                        print(element)
                        print(element[-1])
                        print(element[-2])
                    
                    if element[-2]:
                        _temp.append(element[-1])
                    
                output_data[item] = combined_waves[item]
                output_data_results[item] = element
                output_data_results[item][-1] = _temp
                
            else:
            
                for element in combined_waves_results[item]:
                    if debug_flag:
                        print("______ len(combined_waves_results[item]) == 1:")
                        print(element)
                        print(element[-1])
                        print(element[-2])
                    
                    if element[-2]:
                        output_data[item] = combined_waves[item]
                        output_data_results[item] = element

        if debug_flag:
            print("############################################   temp_combined_waves   ########################################################")
            print("{0:>7} {1:<7} {2:<20} {3:<20} {4:<52} {5:<12} {6:<20}".format('[Index]', '[count]', '[included waves]', '[X]','[Y]', '[t_values]', '[p_values]'))
            for item in combined_waves:
                print("{0:>7} {1:<7} {2:<20} {3:<20} {4:<52} {5:<12} {6:<20}".format(item, combined_waves[item][0], combined_waves[item][1],
                                                                                     combined_waves[item][2],combined_waves[item][3],
                                                                                     combined_waves[item][4],combined_waves[item][5]))
                try:
                    for element in combined_waves_results[item]:
                        print("        {0:<60}".format(element))
                except:
                    pass
            print("##############################################################################################################################")
##
##
##        print("################################################   output_data   #############################################################")
##        print("{0:>7} {1:<7} {2:<20} {3:<20} {4:<52} {5:<12} {6:<20}".format('[Index]', '[count]', '[included waves]', '[X]','[Y]', '[t_values]', '[p_values]'))
##        for item in output_data:
##            print("{0:>7} {1:<7} {2:<20} {3:<20} {4:<52} {5:<12} {6:<20}".format(item, output_data[item][0], output_data[item][1],
##                                                                                 output_data[item][2],output_data[item][3],
##                                                                                 output_data[item][4],output_data[item][5]))
##            try:
##                for element in output_data_results[item]:
##                    print("        {0:<60}".format(element))
##            except:
##                pass
##        print("##############################################################################################################################")
        
        return output_data, output_data_results



############
if __name__ == "__main__":
    datensammlung = EW_testtool_V01.Database()
    simple_lines = EW_testtool_V01.Test(datensammlung.stock_data)
    detail_view_lines = simple_lines.detail_view_lines

    test = TEST(detail_view_lines)


































    
