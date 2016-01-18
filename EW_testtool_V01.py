#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

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

import sys
import EW_fibonacci



################################       
################################
################################
class Database():
    def __init__(self):
        self.stock_data = []
        self.ohlc = []
        
        self.dates = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.volumes = []


        x = 0
        with open('test.csv','r') as csvfile:
            source_data = csv.reader(csvfile, delimiter=str(','))
            for line in source_data:
                #dates.append(mdates.date2num(dt.datetime.strptime(line[0],'%Y%m%d').date()))
                self.dates.append(x)
                self.opens.append(float(line[1]))
                self.highs.append(float(line[2]))
                self.lows.append(float(line[3]))
                self.closes.append(float(line[4]))
                self.volumes.append(int(line[5]))
                
                _temp =  [ #mdates.date2num(dt.datetime.strptime(line[0],'%Y%m%d').date()),
                             x,
                             float(line[1]),
                             float(line[2]),
                             float(line[3]),
                             float(line[4]),
                             int(line[5])
                        ]
                self.ohlc.append(_temp)
                self.stock_data.append(_temp)
                x += 1

################################       
################################
################################
class Test():
    def __init__(self, database):
        self.raw_values = database
        self.db= []
        
        self.main_direction = []
        self.sub_direction = []
        self.final_direction = []
        self.item_marker = []
        self.bar_color = []

        self.list_aussenstab = []
        self.list_innenstab = []
        
        for item in self.raw_values:
            _temp = [ item[1],item[2],item[3],item[4] ]
            self.db.append(_temp)
            
            self.main_direction.append([])
            self.sub_direction.append([])
            self.final_direction.append([])
            self.item_marker.append([[],[],[]])
            self.bar_color.append([])

        print('Database entries:', len(self.db))
        print('########################################################################################################################')
        self.main_dir_classification()
        self.sub_dir_classification()
        self.final_dir_classification()
        self.create_innenstaebe()
        self.create_test_lines()

        self.detail_view()

        print('########################################################################################################################')
        print("{0:>5}  {1:<20} {2:<25} {3:<10} {4:<10} {5:<40}".format("Index","main_dir","sub_dir","final_dir","bar_color","item_marker"))
        for item in range(len(self.db)):
            print("{0:>5}  {1:20} {2:<25} {3:<10} {4:<10} {5:<40}".format(item,self.main_direction[item],self.sub_direction[item],self.final_direction[item],self.bar_color[item],self.item_marker[item]))
        print('########################################################################################################################')
        ###########################
        
##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
    def main_dir_classification(self):
        result = []

        # Step1: check direction, and classify items
        for item in range(len(self.db)):
            #Step0: Classify if item is red or green bar
            self.bar_color[item] = self.check_bar_color(item)
            
            if item == 0:
                    self.main_direction[item] = []
                    self.sub_direction[item] = []
                    self.item_marker[item] = [[],[],[],[]]
            else:
                #Step1.1 check if the list aussenstab already exists and check item for innenstab
                if self.list_aussenstab:
                    self.check_list_aussenstab(item)
                    
                #Step1.2 mark the relevant items if true
                # this will already be done in Step1.1 "check_list_aussenstab"

                #Step1.3 check if Innenstab and if true attach item to list
                result = self.check_direction(self.db[item-1], self.db[item])
                result2 = self.check_innenstab(result)
                
                #Step1.4 mark the relevant items if true
                if result2:
                    self.mark_items(item-1, item)
                    
                #Step1.5 set main_direction
                self.main_direction[item] = result
                #print('==>',item, ' direction:',self.main_direction[item],' sub_direction:', self.sub_direction[item],' item_marker:', self.item_marker[item])

   
    def check_direction(self, index1, index2):
        result = []
        
        if self.get_minimum(index2) == self.get_minimum(index1):
            result.append(str("same_min"))
            
        if self.get_maximum(index2) == self.get_maximum(index1):
            result.append(str("same_max"))
            
        if self.get_minimum(index2) < self.get_minimum(index1):
            result.append(str("down"))
            #print(self.get_minimum(index2), self.get_minimum(index1), result)
            
        if self.get_maximum(index2) > self.get_maximum(index1):
            result.append(str("up"))
            #print(self.get_maximum(index2), self.get_maximum(index1), result)
            
        return result


    def check_innenstab(self, result):
        # check if the current item is Innenstab of the other item 
        if not result or (("same_min" in result or "same_max" in result) and len(result)==1):
            return True
        # else kein Innenstab
        else:                   
            return False       

    def mark_items(self,item1,item2):
        """
        # item_marker [ [0], [[1][0], [1][1]], [2] ]
        # - [0]     Aussenstab
        # - [1][0]  verschachtelung des Innenstabs 
        # - [1][1]  Zuordnung zum Aussenstab
        # - [2]     lfd. Nummer des Innenstabs
        """
        if item1 not in self.list_aussenstab:
            self.list_aussenstab.insert(0, item1)
        if item2 not in self.list_innenstab:    
            self.list_innenstab.insert(0, item2)

        _temp = str("Aussenstab")
        self.item_marker[item1][0] = _temp

        _counter = self.item_marker[item2-1][2]  # take counter value from item before item2 !!!
        if _counter:
            _counter += 1
        else:
            _counter = 1
        _temp = [str("Innenstab"), item1]
        self.item_marker[item2][1] = _temp
        self.item_marker[item2][2] = _counter        


    def check_list_aussenstab(self, index):
        # check if already aussenstab in list
        items_to_delete = []

        #print('_________START check_list_aussenstab: index=',index)
        #print('self.list_aussenstab',self.list_aussenstab)
        
        for item in range(len(self.list_aussenstab)):
            #print('item', item, 'self.list_aussenstab[item]', self.list_aussenstab[item])
            result = self.check_direction(self.db[self.list_aussenstab[item]], self.db[index])
            result2 = self.check_innenstab(result)
            #print('result', result, 'result2', result2)
            
            # If innenstab from Aussenstab in List:
            if result2:
                self.mark_items(self.list_aussenstab[item], index)

            else:
                items_to_delete.append(self.list_aussenstab[item])

        #print('items_to_delete', items_to_delete, 'self.list_aussenstab',self.list_aussenstab)
        for item in items_to_delete:
            self.list_aussenstab.remove(item)

        #print('self.list_aussenstab',self.list_aussenstab)


    def get_minimum(self, list_):
        return min(list_)

    def get_maximum(self, list_):
        return max(list_)

    def check_bar_color(self, item_):
        """   self.db ==> O H L C   """
        if self.db[item_][0] < self.db[item_][3]:
            return str("green")
        else:
            return str("red")

##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
    def sub_dir_classification(self):
        """
        # item_marker [ [0], [[1][0], [1][1]], [2] ]
        # - [0]     Aussenstab
        # - [1][0]  verschachtelung des Innenstabs 
        # - [1][1]  Zuordnung zum Aussenstab
        # - [2]     lfd. Nummer des Innenstabs

        # sub_direction [0, 1, 2, 3, 4, 5]
        # 0 = direction set in testcase1
        # 1 = direction set in testcase2
        # 2 = direction set in testcase3
        # 3 = direction set in the 2nd loop (variable = _loop_inidcator)
        # 4 = direction set in the 3nd loop (variable = _loop_inidcator)
        # 5 = direction set in the 4nd loop (variable = _loop_inidcator)
        
        self.main_direction
        self.db ==> O H L C
        """
        
        self.mark_4later = []
        self.missing_dir = []
        mark_2_delete = []

        _loop_inidcator = 0 # indexoffset for sub_direction to get the right index in a 2nd loop
        for item in range(len(self.main_direction)):
            self.sub_direction[item] = [str(),str(),str(),str(),str(),str(),str(),str()]   # create an empty entry
            self.subdir_testcase1(item, _loop_inidcator)
            self.subdir_testcase2(item, _loop_inidcator)
            self.subdir_testcase3(item, _loop_inidcator)
            #print("{0:>5}  {1:20} {2:<15} {3:<40}".format(item,self.main_direction[item],self.sub_direction[item],self.item_marker[item]))
            
        #print('_______self.mark_4later that could not be finished in 1st loop!!!!:',len(self.mark_4later), self.mark_4later)
        
        mark_2_delete = []
        _loop_inidcator = 3 # indexoffset for sub_direction to get the right index in a 2nd loop
        for item in range(len(self.mark_4later)):
            #print('try to fix self.mark_4later: start', item, self.mark_4later[item], self.sub_direction[self.mark_4later[item]])
            self.subdir_testcase1(self.mark_4later[item], _loop_inidcator)
            #print('try to fix self.mark_4later: case1 done', item, self.mark_4later[item], self.sub_direction[self.mark_4later[item]])
            self.subdir_testcase2(self.mark_4later[item], _loop_inidcator)
            #print('try to fix self.mark_4later: case2 done', item, self.mark_4later[item], self.sub_direction[self.mark_4later[item]])
            self.subdir_testcase3(self.mark_4later[item], _loop_inidcator)
            #print('try to fix self.mark_4later: case3 done', item, self.mark_4later[item], self.sub_direction[self.mark_4later[item]])
            
            if self.sub_direction[self.mark_4later[item]][_loop_inidcator]:
                print(self.mark_4later[item], _loop_inidcator, self.sub_direction[self.mark_4later[item]])
                mark_2_delete.append(self.mark_4later[item])
                
        for item in mark_2_delete:
            self.mark_4later.remove(item)
            
        #print('_______self.mark_4later that could not be finished in 2nd loop!!!!:',len(self.mark_4later), self.mark_4later)
        
        mark_2_delete = []
        _loop_inidcator = 4 # indexoffset for sub_direction to get the right index in a 2nd loop
        for item in range(len(self.mark_4later)):
            #print('try to fix self.mark_4later: start', item, self.mark_4later[item], self.sub_direction[self.mark_4later[item]])
            self.subdir_testcase1(self.mark_4later[item], _loop_inidcator)
            #print('try to fix self.mark_4later: case1 done', item, self.mark_4later[item], self.sub_direction[self.mark_4later[item]])
            self.subdir_testcase2(self.mark_4later[item], _loop_inidcator)
            #print('try to fix self.mark_4later: case2 done', item, self.mark_4later[item], self.sub_direction[self.mark_4later[item]])
            self.subdir_testcase3(self.mark_4later[item], _loop_inidcator)
            #print('try to fix self.mark_4later: case3 done', item, self.mark_4later[item], self.sub_direction[self.mark_4later[item]])
            
            if self.sub_direction[self.mark_4later[item]][_loop_inidcator]:
                print(self.mark_4later[item], _loop_inidcator, self.sub_direction[self.mark_4later[item]])
                mark_2_delete.append(self.mark_4later[item])

        for item in mark_2_delete:
            self.mark_4later.remove(item)
        #print('_______self.mark_4later that could not be finished in 3rd loop!!!!:',len(self.mark_4later), self.mark_4later)
        
        mark_2_delete = []
        _loop_inidcator = 5 # indexoffset for sub_direction to get the right index in a 2nd loop
        for item in range(len(self.mark_4later)):
            #print('try to fix self.mark_4later: start', item, self.mark_4later[item], self.sub_direction[self.mark_4later[item]])
            self.subdir_testcase1(self.mark_4later[item], _loop_inidcator)
            #print('try to fix self.mark_4later: case1 done', item, self.mark_4later[item], self.sub_direction[self.mark_4later[item]])
            self.subdir_testcase2(self.mark_4later[item], _loop_inidcator)
            #print('try to fix self.mark_4later: case2 done', item, self.mark_4later[item], self.sub_direction[self.mark_4later[item]])
            self.subdir_testcase3(self.mark_4later[item], _loop_inidcator)
            #print('try to fix self.mark_4later: case3 done', item, self.mark_4later[item], self.sub_direction[self.mark_4later[item]])
            
            if self.sub_direction[self.mark_4later[item]][_loop_inidcator]:
                print(self.mark_4later[item], _loop_inidcator, self.sub_direction[self.mark_4later[item]])
                mark_2_delete.append(self.mark_4later[item])
                
        for item in mark_2_delete:
            self.mark_4later.remove(item)
        #print('_______self.mark_4later that could not be finished in 4th loop!!!!:',len(self.mark_4later), self.mark_4later)

        mark_2_delete = []
        _loop_inidcator = 6 # indexoffset for sub_direction to get the right index in a 2nd loop
        for item in range(len(self.mark_4later)):
            #print('try to fix self.mark_4later: start', item, self.mark_4later[item], self.sub_direction[self.mark_4later[item]])
            self.subdir_testcase1(self.mark_4later[item], _loop_inidcator)
            #print('try to fix self.mark_4later: case1 done', item, self.mark_4later[item], self.sub_direction[self.mark_4later[item]])
            self.subdir_testcase2(self.mark_4later[item], _loop_inidcator)
            #print('try to fix self.mark_4later: case2 done', item, self.mark_4later[item], self.sub_direction[self.mark_4later[item]])
            self.subdir_testcase3(self.mark_4later[item], _loop_inidcator)
            #print('try to fix self.mark_4later: case3 done', item, self.mark_4later[item], self.sub_direction[self.mark_4later[item]])
            
            if self.sub_direction[self.mark_4later[item]][_loop_inidcator]:
                print(self.mark_4later[item], _loop_inidcator, self.sub_direction[self.mark_4later[item]])
                mark_2_delete.append(self.mark_4later[item])
                
        for item in mark_2_delete:
            self.mark_4later.remove(item)
        #print('_______self.mark_4later that could not be finished in 5th loop!!!!:',len(self.mark_4later), self.mark_4later)

        mark_2_delete = []
        _loop_inidcator = 7 # indexoffset for sub_direction to get the right index in a 2nd loop
        for item in range(len(self.mark_4later)):
            #print('try to fix self.mark_4later: start', item, self.mark_4later[item], self.sub_direction[self.mark_4later[item]])
            self.subdir_testcase1(self.mark_4later[item], _loop_inidcator)
            #print('try to fix self.mark_4later: case1 done', item, self.mark_4later[item], self.sub_direction[self.mark_4later[item]])
            self.subdir_testcase2(self.mark_4later[item], _loop_inidcator)
            #print('try to fix self.mark_4later: case2 done', item, self.mark_4later[item], self.sub_direction[self.mark_4later[item]])
            self.subdir_testcase3(self.mark_4later[item], _loop_inidcator)
            #print('try to fix self.mark_4later: case3 done', item, self.mark_4later[item], self.sub_direction[self.mark_4later[item]])
            
            if self.sub_direction[self.mark_4later[item]][_loop_inidcator]:
                print(self.mark_4later[item], _loop_inidcator, self.sub_direction[self.mark_4later[item]])
                mark_2_delete.append(self.mark_4later[item])
                
        for item in mark_2_delete:
            self.mark_4later.remove(item)
        #print('_______self.mark_4later that could not be finished in 6th loop!!!!:',len(self.mark_4later), self.mark_4later)

        ###### summary
        #print("{0:>5}  {1:<20} {2:<15} {3:<15} {4:<40}".format("Index","main_direction","sub_direction","final_direction","item_marker"))
        for item in range(len(self.sub_direction)):
            #print("{0:>5}  {1:20} {2:<15} {3:<15} {4:<40}".format(item,self.main_direction[item],self.sub_direction[item],self.final_direction[item],self.item_marker[item]))
            if not self.sub_direction[item]:
                self.missing_dir.append(item)
        print('_______self.missing_dir:',len(self.missing_dir), self.missing_dir)
        ####################

    def subdir_testcase1(self, item, _loop_inidcator):
        """ The easiest case. Only "up" or "down" available in main_direction"""
        if _loop_inidcator:
            _index = _loop_inidcator
        else:
            _index = 0
        
        if len(self.main_direction[item]) == 1 and ("up" in self.main_direction[item] or "down" in self.main_direction[item]): 
            self.sub_direction[item][_index] = self.main_direction[item][0]

        
    def subdir_testcase2(self, item, _loop_inidcator):       
        """
        main_direction has "up" and "down" available. So we can check main_direction of partners or mark4later

        Soemtimes the bar with 2 entries "up" and "down" needs an extra vertikal line!
        So final direction need 2 entries [start,stop]
        if not stop: the bar is only 1 point on the line, else the bar is a separate line!!!
        test2.csv ==> 1343-1353
        """
        if _loop_inidcator:
            _index = _loop_inidcator
        else:
            _index = 1
            
        if len(self.main_direction[item]) == 2 and ("up" in self.main_direction[item] or "down" in self.main_direction[item]):

            if (item+1) < (len(self.db)-1): # fix for last item in list (IndexError)
            
                if ("down" in [element for element in self.sub_direction[item-1] if element]) and (
                    "down" in [element for element in self.sub_direction[item+1] if element]) and (
                    self.get_minimum(self.db[item+1]) < self.get_minimum(self.db[item])) :
                    self.sub_direction[item][_index] = str("up")
                    #print('+++++++++++++++++++++Pfad1',item, self.get_minimum(self.db[item+1]), self.get_minimum(self.db[item]))
                    
                elif ("down" in [element for element in self.sub_direction[item-1] if element]) and (
                    "down" in [element for element in self.sub_direction[item+1] if element]) and (
                    self.get_minimum(self.db[item+1]) > self.get_minimum(self.db[item])) :
                    self.sub_direction[item][_index] = str("down")
                    #print('+++++++++++++++++++++Pfad2',item, self.get_minimum(self.db[item+1]), self.get_minimum(self.db[item]))
                    
                elif ("up" in [element for element in self.sub_direction[item-1] if element]) and (
                    "up" in [element for element in self.sub_direction[item+1] if element]) and (
                    self.get_maximum(self.db[item+1]) > self.get_maximum(self.db[item])) :
                    self.sub_direction[item][_index] = str("down")
                    #print('+++++++++++++++++++++Pfad3',item, self.get_minimum(self.db[item+1]), self.get_minimum(self.db[item]))

                elif ("up" in [element for element in self.sub_direction[item-1] if element]) and (
                    "up" in [element for element in self.sub_direction[item+1] if element]) and (
                    self.get_maximum(self.db[item+1]) < self.get_maximum(self.db[item])) :
                    self.sub_direction[item][_index] = str("up")
                    #print('+++++++++++++++++++++Pfad4',item, self.get_minimum(self.db[item+1]), self.get_minimum(self.db[item]))



                elif ("up" in [element for element in self.sub_direction[item-1] if element]) and (
                    self.get_maximum(self.db[item+1]) < self.get_maximum(self.db[item])) :
                    self.sub_direction[item][_index] = str("up")
                    #print('+++++++++++++++++++++Pfad5',item, self.get_minimum(self.db[item+1]), self.get_minimum(self.db[item]))
                elif ("down" in [element for element in self.sub_direction[item-1] if element]) and (
                    self.get_minimum(self.db[item+1]) > self.get_minimum(self.db[item])) :
                    self.sub_direction[item][_index] = str("down")
                    #print('+++++++++++++++++++++Pfad6',item, self.get_minimum(self.db[item+1]), self.get_minimum(self.db[item]))



                elif "down" in [element for element in self.sub_direction[item+1] if element] :
                    self.sub_direction[item][_index] = str("up")
                    #print('+++++++++++++++++++++++++++',item, 'Pfad 7')
     
                elif "up" in [element for element in self.sub_direction[item+1] if element] :
                    self.sub_direction[item][_index] = str("down")
                    #print('+++++++++++++++++++++++++++',item, 'Pfad 8')

                else:
                    if item not in self.mark_4later:
                        self.mark_4later.append(item)
                        #print('===> mark_4later case detected:  index:', item, self.main_direction[item])
                    else:
                        print('==> no direction found for item:', item)

            else:
                #### new
                if "down" in [element for element in self.sub_direction[item-1] if element] :
                    self.sub_direction[item][_index] = str("down")
                    #print('+++++++++++++++++++++++++++',item, 'Pfad 7')

                elif "up" in [element for element in self.sub_direction[item-1] if element] :
                    self.sub_direction[item][_index] = str("up")
                    #print('+++++++++++++++++++++++++++',item, 'Pfad 8')
                                 
                else:
                    if item not in self.mark_4later:
                        self.mark_4later.append(item)
                        #print('===> mark_4later case detected:  index:', item, self.main_direction[item])
                    else:
                        print('==> no direction found for item:', item)


    def subdir_testcase3(self, item, _loop_inidcator):
        """ main_direction not available. So we can check sub_direction of partners or mark4later
            Or Main direction is same_max or same_min.
        """
        if _loop_inidcator:
            _index = _loop_inidcator
        else:
            _index = 2
        
        if not self.main_direction[item] or (len(self.main_direction[item]) == 1 and ("same_max" in self.main_direction[item] or "same_min" in self.main_direction[item])):
            
            if len(self.main_direction[item-1]) == 1 and "up" in self.main_direction[item-1]:
                self.sub_direction[item][_index] = str("down")
            elif len(self.main_direction[item-1]) == 1 and "down" in self.main_direction[item-1]:
                self.sub_direction[item][_index] = str("up")
            elif "up" in [element for element in self.sub_direction[item-1] if element]:
                self.sub_direction[item][_index] = str("down")
            elif "down" in [element for element in self.sub_direction[item-1] if element]:
                self.sub_direction[item][_index] = str("up")          

            else:
                if item not in self.mark_4later:
                    self.mark_4later.append(item)
                    #print('===> mark_4later case detected:  index:', item, self.sub_direction[item])
                else:
                    print('==> no direction found for item:', item)                
                
            if (item+1) < (len(self.db)-1): # fix for last item in list (IndexError)

                if not [element for element in self.sub_direction[item-1] if element] and (self.get_maximum(self.db[item+1]) > self.get_maximum(self.db[item])) and ("up" in [element for element in self.sub_direction[item+1] if element]):
                    self.sub_direction[item][_index] = str("down")
                elif not [element for element in self.sub_direction[item-1] if element] and (self.get_minimum(self.db[item+1]) < self.get_maximum(self.db[item])) and ("down" in [element for element in self.sub_direction[item+1] if element]):
                    self.sub_direction[item][_index] = str("up")
                    
                elif ("up" in [element for element in self.sub_direction[item+1] if element]) and (self.get_maximum(self.db[item+1]) > self.get_maximum(self.db[item])):
                    self.sub_direction[item][_index] = str("up")
                elif ("up" in [element for element in self.sub_direction[item+1] if element]) and (self.get_maximum(self.db[item+1]) < self.get_maximum(self.db[item])):
                    self.sub_direction[item][_index] = str("down")
                    
                elif ("down" in [element for element in self.sub_direction[item+1] if element]) and (self.get_minimum(self.db[item+1]) < self.get_minimum(self.db[item])):
                    self.sub_direction[item][_index] = str("down")
                elif ("down" in [element for element in self.sub_direction[item+1] if element]) and (self.get_minimum(self.db[item+1]) > self.get_minimum(self.db[item])):
                    self.sub_direction[item][_index] = str("up")         

                else:
                    if item not in self.mark_4later:
                        self.mark_4later.append(item)
                        #print('===> mark_4later case detected:  index:', item, self.sub_direction[item])
                    else:
                        print('==> no direction found for item:', item)

##################################################################################################################################
##################################################################################################################################
##################################################################################################################################        
    def final_dir_classification(self):
        """ Sets final direction according to main_direction and sub_direction entries """
        for item in range(len(self.final_direction)):
            
            if [element for element in self.sub_direction[item] if element]:
                self.final_direction[item] = [element for element in self.sub_direction[item] if element][0]
            else:
                print('==> no direction found! Temporary use ==>  "up"  for item!', item)
                self.final_direction[item] = str("up")  # !!!!!!!!!!!!!!!!

##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
    def create_innenstaebe(self):
        self.aussenstaebe_up_lim = {}
        self.aussenstaebe_low_lim = {}

        for item in range(len(self.item_marker)):
            if self.item_marker[item][0]:
                self.aussenstaebe_up_lim[item] = [[],[]]
                self.aussenstaebe_low_lim[item] = [[],[]]

                _temp2 = self.get_maximum(self.db[item])
                self.aussenstaebe_up_lim[item][0].append(item)
                self.aussenstaebe_up_lim[item][1].append(_temp2)

                _temp2 = self.get_minimum(self.db[item])
                self.aussenstaebe_low_lim[item][0].append(item)
                self.aussenstaebe_low_lim[item][1].append(_temp2)
                                
##                print(item)
##                print('aussenstaebe_up_lim', self.aussenstaebe_up_lim[item], self.get_maximum(self.db[item]))
##                print('aussenstaebe_low_lim',self.aussenstaebe_low_lim[item],self.get_minimum(self.db[item]))
                
            try:
                if self.item_marker[item][1][1]:
                    _temp = self.item_marker[item][1][1]
                    #print('______try Pfad: _temp',_temp, 'item', item)

                    _temp2 = self.get_maximum(self.db[_temp])
                    self.aussenstaebe_up_lim[_temp][0].append(item)
                    self.aussenstaebe_up_lim[_temp][1].append(_temp2)
                                
                    _temp2 = self.get_minimum(self.db[_temp])
                    self.aussenstaebe_low_lim[_temp][0].append(item)
                    self.aussenstaebe_low_lim[_temp][1].append(_temp2)

##                print(self.db[item])
##                print('aussenstaebe_up_lim', self.aussenstaebe_up_lim[_temp], self.get_maximum(self.db[item]))
##                print('aussenstaebe_low_lim',self.aussenstaebe_low_lim[_temp],self.get_minimum(self.db[item]))
                
            except IndexError:
                pass
            except:
                (type, value, traceback) = sys.exc_info()
                print("Unexpected error:")
                print("Type: ", type)
                print("Value: ", value)
                print("traceback: ", traceback)
                raise


##        for item in self.aussenstaebe_up_lim:
##            print('aussenstaebe_up_lim:', item, self.aussenstaebe_up_lim[item])
##        for item in self.aussenstaebe_low_lim:
##            print('aussenstaebe_low_lim:', item, self.aussenstaebe_low_lim[item])           
##        print('aussenstaebe_up_lim:',self.aussenstaebe_up_lim)
##        print('aussenstaebe_low_lim:',self.aussenstaebe_low_lim)

##################################################################################################################################
##################################################################################################################################
##################################################################################################################################        
    def create_test_lines(self):
        """ Creates lines in the graph
        self.line_dict = {[0, 1, 2]}
        0 = final_direction
        1 = start point of the line
        2 = end point of the line

        self.line_coords = {[x], [y]}
        # If direction == 'up' Start is Minimum and End is Maximum of the Index
        """
        self.line_dict = {}
        self.line_coords = {}


        self.parse_directions()


    def parse_directions(self):
        act_key = False
        last_key = False
        line_id = 0
        line_in_progress = False

        #print("{0:>5} {1:>10}    {2:<25}  {3:<20}".format("Index","key","line_dict","line_coords"))
        
        for item in range(1,len(self.final_direction)):
            act_key = self.final_direction[item]
            
            # Step1.1: If line_in_progress: search for a changing direction to add the end point to the dict
            # Step1.2: If last item and line_in_progress 0==> also add the end point in the dict          
            if (act_key != last_key or item == len(self.final_direction)-1) and line_in_progress:
                line_in_progress = False
                
                if item != len(self.final_direction)-1: #Fix for last item
                    self.line_dict[line_id][2] = item-1 #Save the last item with the same direction and not with the new one!
                else:
                    self.line_dict[line_id][2] = item   #Fix for last item
                
                # Step1.3: Also Create a item in the line_coords dict for creating a graph
                # If direction == 'up': the end the maximum
                # If direction == 'down': the end the minimum
                if self.line_dict[line_id][0] == 'up':
                    _index = self.line_dict[line_id][2]
                    _list = self.db[_index]
                    _end = self.get_maximum(_list)
                    self.line_coords[line_id][0].append(_index)
                    self.line_coords[line_id][1].append(_end)
                    
                elif self.line_dict[line_id][0] == 'down':
                    _index = self.line_dict[line_id][2]
                    _list = self.db[_index]
                    _end = self.get_minimum(_list)
                    self.line_coords[line_id][0].append(_index)
                    self.line_coords[line_id][1].append(_end)
                #print("{0:>5} {1:>10}    {2:<25}  {3:<20}".format(item,line_id,self.line_dict[line_id],self.line_coords[line_id]))    


            # Step2: Create a new entry in the dict with direction and start point
            if act_key != last_key and not line_in_progress:
                line_in_progress = True
                line_id += 1
                
                # Step2.1: Start is the end point of the last line!
                self.line_dict[line_id] = [self.final_direction[item], item-1, 0]  


                # Step2.2: Also Create a item in the line_coords dict for creating a graph
                # If direction == 'up': Start is the minimum of the index and the end the maximum
                # If direction == 'down': Start is the maximum of the index and the end the minimum
                if self.line_dict[line_id][0] == 'up':
                    _index = self.line_dict[line_id][1]
                    _list = self.db[_index]
                    _start = self.get_minimum(_list)
                    self.line_coords[line_id] = [[_index], [_start]]
                    
                elif self.line_dict[line_id][0] == 'down':
                    _index = self.line_dict[line_id][1]
                    _list = self.db[_index]
                    _start = self.get_maximum(_list)
                    self.line_coords[line_id] = [[_index], [_start]]


            # Step3: last_key = act_key and start next cycle
            last_key = act_key

    
        #print('_______self.line_dict:',len(self.line_dict), self.line_dict)
##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
    def detail_view(self):
        """
        self.db ==> O H L C
        """
        self.detail_marker = {}     # ["item": start, end]]
        self.detail_lines = {}      # ["_line_id": [x],[y]]
        self.simple_l1 = {}         # ["_line_id": [x],[y]]
    

        self.detail_step1()
        self.create_detail_lines()
        self.detail_simplifiy_level_1()

    def detail_step1(self):
        for item in range(len(self.db)):
            if self.bar_color[item] == "green":
                self.detail_marker[item] = str("down"), str("up")    #self.get_minimum(self.db[item]), self.get_macimum(self.db[item])
            elif self.bar_color[item] == "red":
                self.detail_marker[item] = str("up"), str("down")
            else:
                print('=======>>> Error color_bar for item:', item)

            #print(item, self.bar_color[item], self.detail_marker[item])



    def create_detail_lines(self):
        _line_id = 0

        for item in range(len(self.detail_marker)):
            _line_id += 1

            if item == 0:
                if self.bar_color[item] == "green":
                    self.detail_lines[_line_id] = [[item,item], [self.get_minimum(self.db[item]),self.get_maximum(self.db[item])]]
                else:
                    self.detail_lines[_line_id] = [[item,item], [self.get_maximum(self.db[item]),self.get_minimum(self.db[item])]]
                #print(item, self.detail_lines[_line_id], 'self.bar_color[item]',self.bar_color[item])
            
            else:
                if self.bar_color[item-1] == "green" and self.bar_color[item] == "green":
                    self.detail_lines[_line_id] = [[item-1,item], [self.get_maximum(self.db[item-1]),self.get_minimum(self.db[item])]]
                elif self.bar_color[item-1] == "green" and self.bar_color[item] == "red":
                    self.detail_lines[_line_id] = [[item-1,item], [self.get_maximum(self.db[item-1]),self.get_maximum(self.db[item])]]
                if self.bar_color[item-1] == "red" and self.bar_color[item] == "green":
                    self.detail_lines[_line_id] = [[item-1,item], [self.get_minimum(self.db[item-1]),self.get_minimum(self.db[item])]]
                elif self.bar_color[item-1] == "red" and self.bar_color[item] == "red":
                    self.detail_lines[_line_id] = [[item-1,item], [self.get_minimum(self.db[item-1]),self.get_maximum(self.db[item])]]
                #print(item, self.detail_lines[_line_id],'self.bar_color[item-1]',self.bar_color[item-1], 'self.bar_color[item]',self.bar_color[item])
            
                _line_id += 1
                if self.bar_color[item] == "green":
                    self.detail_lines[_line_id] = [[item,item], [self.get_minimum(self.db[item]),self.get_maximum(self.db[item])]]
                else:
                    self.detail_lines[_line_id] = [[item,item], [self.get_maximum(self.db[item]),self.get_minimum(self.db[item])]]
                #print(item, self.detail_lines[_line_id], 'self.bar_color[item]',self.bar_color[item])
                
        #for item in self.detail_lines:
        #    print(item, self.detail_lines[item])


    def detail_simplifiy_level_1(self):
        """ self.simple_l1 = [0, 1 , 2]
        0 = color of the 1st bar
        1 = direction of the line
        2 = x points [start,end]
        3 = y points [start,end]

        Step1: Close old line at current item
        Step2: Open new line at current item
        Step3: if necessary close line at current item
        Step4: If necessary open new line at current item
        Step5: Fix for last item
        """
        self.line_id = 0
        self.line_in_progress = False
        self.line_last_item = 0
        
        for item in range(len(self.db)):
            print('START')
            # Step1 : check if self.line_in_progress and the end point of the line is reached so the line can be closed
            _temp = self.detail_simplifiy_level_1_step1(item)


            # Step2 : Create a new entry with the start point of the line
            if _temp or item == 0:
                _temp = self.detail_simplifiy_level_1_step2(item)

            
            # Step3 : If necessary close line at current item
            if _temp:
                _temp = self.detail_simplifiy_level_1_step3(item)


            # Step4 : If necessary open new line at current item
            if _temp:
                _temp = self.detail_simplifiy_level_1_step4(item)
            

            # Step5 : Fix for the last item
            if item == (len(self.db)-1):
                self.detail_simplifiy_level_1_close_last_item(item)


        for item in self.simple_l1:
            print("{0:>5}  {1:10} {2:<10} {3:<10} {4:<10}".format(item, self.simple_l1[item][0],self.simple_l1[item][1],self.simple_l1[item][2],self.simple_l1[item][3]))


###################################
    def detail_simplifiy_level_1_step1(self,item):
        """ Step1 : check if self.line_in_progress and the end point of the line is reached so the line can be closed """
        if item != 0 and item != (len(self.db)-1):
            
            # if direction == "up" ==> Find the maximum of the line
            if self.line_in_progress and self.simple_l1[self.line_id][1] == "up" and (
                self.get_maximum(self.db[item+1]) < self.get_maximum(self.db[item])):
                
                self.line_in_progress = False
                self.simple_l1[self.line_id][2].append(item)
                self.simple_l1[self.line_id][3].append(self.get_maximum(self.db[item]))
                self.line_last_item = item
                print('Step1_1:',item, self.line_id, self.line_in_progress, self.simple_l1[self.line_id])
                return True
            # if direction == "down" ==> Find the minimum of the line
            elif self.line_in_progress and self.simple_l1[self.line_id][1] == "down" and (
                self.get_minimum(self.db[item+1]) > self.get_minimum(self.db[item])):
                
                self.line_in_progress = False
                self.simple_l1[self.line_id][2].append(item)
                self.simple_l1[self.line_id][3].append(self.get_minimum(self.db[item]))
                self.line_last_item = item
                print('Step1_2:',item, self.line_id, self.line_in_progress, self.simple_l1[self.line_id])
                return True


            # if direction == "up" ==> stop when this bar has a lower minimum then the one before
            elif self.line_in_progress and self.simple_l1[self.line_id][1] == "up" and (
                self.get_minimum(self.db[item]) < self.get_minimum(self.db[item-1])):
                
                self.line_in_progress = False
                self.simple_l1[self.line_id][2].append(item)
                self.simple_l1[self.line_id][3].append(self.get_maximum(self.db[item]))
                self.line_last_item = item
                print('Step1_3:',item, self.line_id, self.line_in_progress, self.simple_l1[self.line_id])
                return True                                          
            # if direction == "down" ==> stop when this bar has a higher maximum then the one before
            elif self.line_in_progress and self.simple_l1[self.line_id][1] == "down" and (
                self.get_maximum(self.db[item]) > self.get_maximum(self.db[item-1])):
                
                self.line_in_progress = False
                self.simple_l1[self.line_id][2].append(item)
                self.simple_l1[self.line_id][3].append(self.get_minimum(self.db[item]))
                self.line_last_item = item
                print('Step1_4:',item, self.line_id, self.line_in_progress, self.simple_l1[self.line_id])
                return True  


            # if direction == "up" ==> stop when this bar has a higher minimum than item+1 and color[item+1] == "green"
            elif self.line_in_progress and self.simple_l1[self.line_id][1] == "up" and (
                self.get_minimum(self.db[item+1]) < self.get_minimum(self.db[item])) and (
                self.bar_color[item+1] == "green"):
                
                self.line_in_progress = False
                self.simple_l1[self.line_id][2].append(item)
                self.simple_l1[self.line_id][3].append(self.get_maximum(self.db[item]))
                self.line_last_item = item
                print('Step1_6:',item, self.line_id, self.line_in_progress, self.simple_l1[self.line_id])
                return True 

            # if direction == "down" ==> stop when this bar has a lower maximum than item+1 and color[item+1] == "red"
            elif self.line_in_progress and self.simple_l1[self.line_id][1] == "down" and (
                self.get_maximum(self.db[item+1]) > self.get_maximum(self.db[item])) and (
                self.bar_color[item+1] == "red"):
                
                self.line_in_progress = False
                self.simple_l1[self.line_id][2].append(item)
                self.simple_l1[self.line_id][3].append(self.get_minimum(self.db[item]))
                self.line_last_item = item
                print('Step1_6:',item, self.line_id, self.line_in_progress, self.simple_l1[self.line_id])
                return True 
    
            else:

                print('Step1_9:',item, self.line_id, self.line_in_progress, self.simple_l1[self.line_id])
                return False

        
            
    def detail_simplifiy_level_1_step2(self,item):
        """ Step2: Open new line at current item """
        if item == 0:

            if not self.line_in_progress and self.bar_color[item] == "green":
                self.line_id += 1
                self.line_in_progress = True
                self.simple_l1[self.line_id] = [str("green"),str("up"),[item],[self.get_minimum(self.db[item])]]
                self.line_last_item = item
                print('Step2_1:',item, self.line_id, self.line_in_progress, self.simple_l1[self.line_id])
                return True
            
            elif not self.line_in_progress and self.bar_color[item] == "red":
                self.line_id += 1
                self.line_in_progress = True
                self.simple_l1[self.line_id] = [str("red"),str("down"),[item],[self.get_maximum(self.db[item])]]
                self.line_last_item= item
                print('Step2_2:',item, self.line_id, self.line_in_progress, self.simple_l1[self.line_id])
                return True
             
        else:
            
            if not self.line_in_progress and self.simple_l1[self.line_id][1] == "up":
                self.line_id += 1
                self.line_in_progress = True
                self.simple_l1[self.line_id] = [self.bar_color[item],str("down"),[item],[self.get_maximum(self.db[item])]]
                self.line_last_item = item
                print('Step2_3:',item, self.line_id, self.line_in_progress, self.simple_l1[self.line_id])
                return True
            
            elif not self.line_in_progress and self.simple_l1[self.line_id][1] == "down":
                self.line_id += 1
                self.line_in_progress = True
                self.simple_l1[self.line_id] = [self.bar_color[item],str("up"),[item],[self.get_minimum(self.db[item])]]
                self.line_last_item = item
                print('Step2_4:',item, self.line_id, self.line_in_progress, self.simple_l1[self.line_id])
                return True
               
        


    def detail_simplifiy_level_1_step3(self,item):
        """ Step3 : If necessary close line at current item """
        if item != 0 and item != (len(self.db)-1):

            if self.line_in_progress and self.simple_l1[self.line_id][1] == "up" and (
                self.get_maximum(self.db[item+1]) < self.get_maximum(self.db[item])) and not self.bar_color[item] == "red":
                    self.line_in_progress = False
                    self.simple_l1[self.line_id][2].append(item)
                    self.simple_l1[self.line_id][3].append(self.get_maximum(self.db[item]))
                    self.line_last_item = item
                    print('Step3_1:',item, self.line_id, self.line_in_progress, self.simple_l1[self.line_id])
                    return True
            
            elif self.line_in_progress and self.simple_l1[self.line_id][1] == "down" and (
                self.get_minimum(self.db[item+1]) > self.get_minimum(self.db[item])) and not self.bar_color[item] == "green":
                    self.line_in_progress = False
                    self.simple_l1[self.line_id][2].append(item)
                    self.simple_l1[self.line_id][3].append(self.get_minimum(self.db[item]))
                    self.line_last_item = item
                    print('Step3_2:',item, self.line_id, self.line_in_progress, self.simple_l1[self.line_id])
                    return True
                
            else:
                print('Step3_3:',item, self.line_id, self.line_in_progress, self.simple_l1[self.line_id])
                return False
                

        

    def detail_simplifiy_level_1_step4(self,item):
        """ # Step4 : If necessary open new line at current item """
        if item == 0:
            if not self.line_in_progress and self.bar_color[item] == "green":
                self.line_id += 1
                self.line_in_progress = True
                self.simple_l1[self.line_id] = [str("green"),str("up"),[item],[self.get_minimum(self.db[item])]]
                self.line_last_item = item
                print('Step4_1:',item, self.line_id, self.line_in_progress, self.simple_l1[self.line_id])
                return True
                
            elif not self.line_in_progress and self.bar_color[item] == "red":
                self.line_id += 1
                self.line_in_progress = True
                self.simple_l1[self.line_id] = [str("red"),str("down"),[item],[self.get_maximum(self.db[item])]]
                self.line_last_item= item
                print('Step4_2:',item, self.line_id, self.line_in_progress, self.simple_l1[self.line_id])
                return True
             
        else:
            if not self.line_in_progress and self.simple_l1[self.line_id][1] == "up":
                self.line_id += 1
                self.line_in_progress = True
                self.simple_l1[self.line_id] = [self.bar_color[item],str("down"),[item],[self.get_maximum(self.db[item])]]
                self.line_last_item = item
                print('Step4_3:',item, self.line_id, self.line_in_progress, self.simple_l1[self.line_id])
                return True
            
            elif not self.line_in_progress and self.simple_l1[self.line_id][1] == "down":
                self.line_id += 1
                self.line_in_progress = True
                self.simple_l1[self.line_id] = [self.bar_color[item],str("up"),[item],[self.get_minimum(self.db[item])]]
                self.line_last_item = item
                print('Step4_4:',item, self.line_id, self.line_in_progress, self.simple_l1[self.line_id])
                return True
                
                


    def detail_simplifiy_level_1_close_last_item(self,item):
        if self.line_in_progress and self.bar_color[item] and self.bar_color[item] == "green":        
            self.line_in_progress = False
            self.simple_l1[self.line_id][2].append(item)
            self.simple_l1[self.line_id][3].append(self.get_maximum(self.db[item]))
        elif self.line_in_progress and self.bar_color[item] and self.bar_color[item] == "red":
            self.line_in_progress = False
            self.simple_l1[self.line_id][2].append(item)
            self.simple_l1[self.line_id][3].append(self.get_minimum(self.db[item]))    

        print('last item:',item, self.line_id, self.line_in_progress, self.simple_l1[self.line_id])
        




##################################################################################################################################
##################################################################################################################################
##################################################################################################################################        

############
if __name__ == "__main__":
    datensammlung = Database()
    horst = Test(datensammlung.stock_data)


