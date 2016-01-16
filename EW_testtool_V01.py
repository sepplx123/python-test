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
class Classification():
    def __init__(self,index):
        self.index = index        
        self.main_direction = []
        self.subdirection = []
        self.item_marker = []



class Innenstab(Classification):
    def __init__(self):
        self.aussenstab_index = 0
        self.innenstab_counter = 0


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

        self.list_aussenstab = []
        self.list_innenstab = []
        
        for item in self.raw_values:
            _temp = [ item[1],item[2],item[3],item[4] ]
            self.db.append(_temp)
            
            self.main_direction.append([])
            self.sub_direction.append([])
            self.final_direction.append([])
            self.item_marker.append([[],[],[]])

        print('Database entries:', len(self.db))
        print('########################################################################################################################')
        self.main_dir_classification()
        self.sub_dir_classification()
        self.final_dir_classification()
        self.create_innenstaebe()
        self.create_test_lines()


        
        for item in range(len(self.db)):
            print("{0:>5}  {1:20} {2:<15} {3:<15} {4:<40}".format(item,self.main_direction[item],self.sub_direction[item],self.final_direction[item],self.item_marker[item]))
        print('########################################################################################################################')
        ###########################
        
##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
    def main_dir_classification(self):
        result = []

        # Step1: check direction, and classify items
        for item in range(len(self.db)):
            if item == 0:
                    self.main_direction[item] = []
                    self.sub_direction[item] = []
                    self.item_marker[item] = [[],[],[]]
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
        
        self.main_direction
        self.sub_direction
        self.item_marker
        self.db ==> O H L C
        """
        self.mark_4later = []
        self.missing_dir = []
        mark_2_delete = []
        
        for item in range(len(self.main_direction)):
            self.subdir_testcase1(item)
            self.subdir_testcase2(item)
            self.subdir_testcase3(item)
            #print("{0:>5}  {1:20} {2:<15} {3:<40}".format(item,self.main_direction[item],self.sub_direction[item],self.item_marker[item]))
            
        print('_______self.mark_4later:',len(self.mark_4later),self.mark_4later)
        print('_______try to fix self.mark_4later items in 2nd check loop:',len(self.mark_4later),self.mark_4later)
        
        for item in range(len(self.mark_4later)):
            #print('try to fix self.mark_4later: start', item, self.mark_4later[item], self.sub_direction[self.mark_4later[item]])
            self.subdir_testcase1(self.mark_4later[item])
            #print('try to fix self.mark_4later: case1', item, self.mark_4later[item], self.sub_direction[self.mark_4later[item]])
            self.subdir_testcase2(self.mark_4later[item])
            #print('try to fix self.mark_4later: case2', item, self.mark_4later[item], self.sub_direction[self.mark_4later[item]])
            self.subdir_testcase3(self.mark_4later[item])
            #print('try to fix self.mark_4later: case3', item, self.mark_4later[item], self.sub_direction[self.mark_4later[item]])

            if self.sub_direction[self.mark_4later[item]]:
                mark_2_delete.append(self.mark_4later[item])
                
        for item in mark_2_delete:
            self.mark_4later.remove(item)
            
        print('_______self.mark_4later that could not be finished!!!!:',len(self.mark_4later), self.mark_4later)


        ###### summary
        #print("{0:>5}  {1:<20} {2:<15} {3:<15} {4:<40}".format("Index","main_direction","sub_direction","final_direction","item_marker"))
        for item in range(len(self.sub_direction)):
        #    print("{0:>5}  {1:20} {2:<15} {3:<15} {4:<40}".format(item,self.main_direction[item],self.sub_direction[item],self.final_direction[item],self.item_marker[item]))
            if not self.sub_direction[item]:
                self.missing_dir.append(item)
        print('_______self.missing_dir:',len(self.missing_dir), self.missing_dir)
        print("{0:>5}  {1:<20} {2:<15} {3:<15} {4:<40}".format("Index","main_direction","sub_direction","final_direction","item_marker"))
        ####################

    def subdir_testcase1(self, item):
        """ The easiest case. Only "up" or "down" available in main_direction"""
        if len(self.main_direction[item]) == 1 and ("up" in self.main_direction[item] or "down" in self.main_direction[item]): 
            self.sub_direction[item] = self.main_direction[item]

        
    def subdir_testcase2(self, item):       
        """ main_direction has "up" and "down" available. So we can check main_direction of partners or mark4later """                
        if len(self.main_direction[item]) == 2 and ("up" in self.main_direction[item] or "down" in self.main_direction[item]):
            
            if len(self.main_direction[item-1]) == 1 and ("up" in self.main_direction[item] or "down" in self.main_direction[item]) and item > 0: 
                self.sub_direction[item] = self.main_direction[item-1]
            elif len(self.main_direction[item+1]) == 1 and ("up" in self.main_direction[item] or "down" in self.main_direction[item]) and item < len(self.main_direction)-1:
                self.sub_direction[item] = self.main_direction[item+1]
            else:
                if item not in self.mark_4later:
                    self.mark_4later.append(item)
                    print('===> mark_4later case detected:  index:', item, self.main_direction[item+1])
                else:
                    print('==> no direction found for item:', item)


    def subdir_testcase3(self, item):
        """ main_direction not available. So we can check sub_direction of partners or mark4later """
        if not self.main_direction[item]:
            if len(self.main_direction[item-1]) == 1 and ("up" in self.main_direction[item] or "down" in self.main_direction[item]) and item > 0:
                self.sub_direction[item] = self.main_direction[item-1]
            elif len(self.main_direction[item+1]) == 1 and ("up" in self.main_direction[item] or "down" in self.main_direction[item]) and item < len(self.main_direction)-1:
                self.sub_direction[item] = self.main_direction[item+1]
            elif self.sub_direction[item-1] and item > 0:
                self.sub_direction[item] = self.sub_direction[item-1]                                                   
            elif self.sub_direction[item+1] and item < len(self.main_direction)-1:
                self.sub_direction[item] = self.sub_direction[item+1]
            else:
                if item not in self.mark_4later:
                    self.mark_4later.append(item)
                    print('===> mark_4later case detected:  index:', item, self.sub_direction[item+1])
                else:
                    print('==> no direction found for item:', item)

##################################################################################################################################
##################################################################################################################################
##################################################################################################################################        
    def final_dir_classification(self):
        """ Sets final direction according to main_direction and sub_direction entries """
        for item in range(len(self.final_direction)):
            if self.sub_direction[item]:
                self.final_direction[item] = self.sub_direction[item]
            else:
                print('==> no direction found for item:', item)

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
        """ Creates lines in the graph """
        pass






            
##################################################################################################################################
##################################################################################################################################
##################################################################################################################################        

############
if __name__ == "__main__":
    datensammlung = Database()
    horst = Test(datensammlung.stock_data)


