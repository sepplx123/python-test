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


def ratio_hi_lo(value_1, value_2):
    """ checks wich value is higher and creates the ratio between
    higher value / lower_value and returns True/False for value_1 or value_2 and the ratio
    
    returned values: value_1>, value_2>, ratio(hi/lo) """
    if value_1 > value_2:
        return True, False, value_1 / value_2
    else:
        return False, True, value_2 / value_1





################################       
################################
################################
class TEST():
    """
    parse the database and try to find valid EW vertexes inside

    ====>>>> Mssing: Step0: Find the start point (Extremum Min or Max) for the following operations
    
    Step1: Combine always the following 3 lines to a zigzag and save it.
    Step2: Send this zigzag to the analyzer modul
    Step3: After the 2nd zigzag is finished we can try to combine the first 2 to a new one.
    Step4: Send the new combined zigzag to the analyzer modul
    Step5: After the 3rd zigzag is finished we can try to combine the first impulse
    Step6: Send the new combined impulse to the analyzer modul

    """
    def __init__(self, data_input):
        """
        data_input = {}   # ["_line_id" : "spare", "direction", [X], [Y]]

        self.basis_waves = {} ==> The following 3 lines on the lowest level 
        self.comb_lvl_1 = {} ==> Combines 2 basis_waves to one with a higher degree.
        
        """
        self.database = data_input
        
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
        _testobject = []
        _result = []

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
                    #===> self.basis_waves[_line_id][4] = [time_values]
                    #===> self.basis_waves[_line_id][5] = [price_values]
                    _testobject = [self.basis_waves[_line_id][4], self.basis_waves[_line_id][5]]
                    #self.basis_waves_results[_line_id] = self.ew_types_abc.check(_testobject)
                    self.basis_waves_results[_line_id] = self.analyzer.analyze(self.basis_waves[_line_id], debug_flag)
                    

                #Step3: After the 2nd zigzag is finished we can try to combine the first 2 basis_waves to a new one ===> comb_lvl_1.
                # This new wave can be either an abc or impulse pattern
                if _line_id == 2 and not _line_in_progress:
                    self.comb_lvl_1, self.comb_lvl_1_results = self.combine_basis_waves(self.basis_waves[_line_id-1], self.basis_waves[_line_id], False)


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




##        print("###############################################   self.basis_waves   ##########################################################")
##        print("{0:>7} {1:<7} {2:<16} {3:<20} {4:<52} {5:<12} {6:<20}".format('[Index]', '[count]', '[included waves]', '[X]','[Y]', '[t_values]', '[p_values]'))
##        for item in self.basis_waves:
##            print("{0:>7} {1:<7} {2:<16} {3:<20} {4:<52} {5:<12} {6:<20}".format(item, self.basis_waves[item][0], self.basis_waves[item][1],
##                                                                                 self.basis_waves[item][2],self.basis_waves[item][3],
##                                                                                 self.basis_waves[item][4],self.basis_waves[item][5]))
##            try:
##                for element in self.basis_waves_results[item]:
##                    print("        {0:<60}".format(element))
##            except:
##                pass
##        print("##############################################################################################################################")
##

            
    def combine_basis_waves(self, wave_1, wave_2, debug_flag):
        """
        basis_wave:                                    ["abc", "a_line - b_line - c_line", [X], [Y], [time_values], [price_values]]
        self.comb_lvl_1 = {}          # { "_line_id" : ["abc", "a_line - b_line - c_line", [X], [Y], [time_values], [price_values]] }
        self.comb_lvl_1_results = {}  # 

        
        Case 1: up direction of a_wave in wave_1 

            Step1: If max(wave2) > max(wave1) we can combine it
            Step2: Find the dominant retracement wave (b_wave in wave_1 or a_wave in wave_2) and create a new abc pattern
                   If both corrective waves are almost equal, we have to create 2 new waves
            Step3: Create an impulse if the basis_waves fit to this pattern

        case 2: down direction of a_wave in wave_1

            Step1: see above
            Step2: see above
            Step3: see above

        Step4: Only valid patterns can be accepted and returned
        """
        
        comb_lvl_1 = {}
        comb_lvl_1_results = {}
        output_data = {}
        output_data_results = {}
        
        _direction = ""
        _dom_wave1 = 0
        _dom_wave2 = 0
        _ratio = 0
        _trigger = 1.5
        _line_id = 0
        _line_in_progress = False

        # create a direction flag of the first wave for further calculation purposes
        if wave_1[3][1] > wave_1[3][0]:
            _direction = str("up")
        else:
            _direction = str("down")



        # Case 1: up direction of a_wave in wave_1
        if _direction == "up":
            
            # Step1: If max(wave2) > max(wave1) we can combine it
            if max(wave_2[3]) > max(wave_1[3]):

                # Step2: Find the dominant retracement wave (b_wave in wave_1 or a_wave in wave_2) and create a new abc pattern
                #        If both corrective waves are almost equal, we have to create 2 new waves
                _dom_wave1, _dom_wave2, _ratio = ratio_hi_lo(wave_1[5][1], wave_2[5][0])


                # Also include time values to decide which one is the dominant retracement wave !!!
                if _dom_wave1 and _ratio >= _trigger and wave_1[4][1] >= wave_2[4][0]:
                    _line_id += 1
                    #_line_in_progress = True                
                    comb_lvl_1[_line_id] = [ str("abc"),
                                            [wave_1[1][0], wave_1[1][1], [wave_1[1][2], wave_2[1][0], wave_2[1][1]] ],
                                            [wave_1[2][0], wave_1[2][1], wave_1[2][2], wave_2[2][2] ],
                                            [wave_1[3][0], wave_1[3][1], wave_1[3][2], wave_2[3][2] ],
                                            [wave_1[4][0], wave_1[4][1], abs(wave_2[2][2] - wave_1[2][2]) +1 ],  # +1 damit man keine 0 im time_value hat
                                            [wave_1[5][0], wave_1[5][1], abs(wave_2[3][2] - wave_1[3][2]) ],
                                           ]
                    # Send these combined waves to the analyzer modul and receive the result
                    comb_lvl_1_results[_line_id] = self.analyzer.analyze(comb_lvl_1[_line_id], debug_flag)


                elif _dom_wave2 and _ratio >= _trigger and wave_2[4][0] >= wave_1[4][1]:
                    _line_id += 1
                    #_line_in_progress = True                
                    comb_lvl_1[_line_id] = [ str("abc"),
                                            [wave_1[1], wave_2[1][0], wave_2[1][1] ],
                                            [wave_1[2][0], wave_1[2][-1], wave_2[2][1], wave_2[2][2] ],
                                            [wave_1[3][0], wave_1[3][-1], wave_2[3][1], wave_2[3][2] ],
                                            [abs(wave_1[2][-1] - wave_1[2][0]) +1, wave_2[4][0], wave_2[4][1] ],  # +1 damit man keine 0 im time_value hat
                                            [abs(wave_1[3][-1] - wave_1[3][0]), wave_2[5][0], wave_2[5][1] ],
                                           ]
                    # Send these combined waves to the analyzer modul and receive the result
                    comb_lvl_1_results[_line_id] = self.analyzer.analyze(comb_lvl_1[_line_id], debug_flag)
                    
                else:
                    pass
                    

                # Step3: Create an impulse/LDT/EDT if the basis_waves fit to this pattern
                _line_id += 1
                #_line_in_progress = True                
                comb_lvl_1[_line_id] = [ str("12345"),
                                        [wave_1[1][0], wave_1[1][1], wave_1[1][2], wave_2[1][0], wave_2[1][1]],
                                        [wave_1[2][0], wave_1[2][1], wave_1[2][2], wave_1[2][3], wave_2[2][1], wave_2[2][2] ],
                                        [wave_1[3][0], wave_1[3][1], wave_1[3][2], wave_1[3][3], wave_2[3][1], wave_2[3][2] ],
                                        [wave_1[4][0], wave_1[4][1], wave_1[4][2], wave_2[4][0], wave_2[4][1] ],
                                        [wave_1[5][0], wave_1[5][1], wave_1[5][2], wave_2[5][0], wave_2[5][1] ],

                                       ]
                # Send these combined waves to the analyzer modul and receive the result              
                comb_lvl_1_results[_line_id] = self.analyzer.analyze(comb_lvl_1[_line_id], debug_flag)




        # Case 2: down direction of a_wave in wave_1
        if _direction == "down":
            pass    






        # Step4: Only valid patterns can be accepted and returned
        # Check all results and only keep valid patterns and add them to the output_data
        for item in comb_lvl_1_results:
            for element in comb_lvl_1_results[item]:
                if element[-2]:
                    output_data[item] = comb_lvl_1[item]
                    output_data_results[item] = element
                    #print(output_data_results[item])


##        print("############################################   temp_comb_lvl_1_waves   ########################################################")
##        print("{0:>7} {1:<7} {2:<20} {3:<20} {4:<52} {5:<12} {6:<20}".format('[Index]', '[count]', '[included waves]', '[X]','[Y]', '[t_values]', '[p_values]'))
##        for item in comb_lvl_1:
##            print("{0:>7} {1:<7} {2:<20} {3:<20} {4:<52} {5:<12} {6:<20}".format(item, comb_lvl_1[item][0], comb_lvl_1[item][1],
##                                                                                 comb_lvl_1[item][2],comb_lvl_1[item][3],
##                                                                                 comb_lvl_1[item][4],comb_lvl_1[item][5]))
##            try:
##                for element in comb_lvl_1_results[item]:
##                    print("        {0:<60}".format(element))
##            except:
##                pass
##        print("##############################################################################################################################")
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


































    
