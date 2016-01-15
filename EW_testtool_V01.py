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

import fibonacci



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
        self.subdirection = []
        self.item_marker = []

        self.list_aussenstab = []
        self.list_innenstab = []
        
        for item in self.raw_values:
            _temp = [ item[1],item[2],item[3],item[4] ]
            self.db.append(_temp)
            
            self.main_direction.append([])
            self.subdirection.append([])
            self.item_marker.append([[],[],[]])

        print('Database entries:', len(self.db))
        print('##############################################################')
        self.test_mainloop()
        for index in range(len(self.db)):
            print('==>',index, self.main_direction[index],self.subdirection[index],self.item_marker[index])
        print('##############################################################')
        ###########################
        
    def get_minimum(self, list_):
        return min(list_)

    def get_maximum(self, list_):
        return max(list_)
      
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
        # Aussenstab [0]
        # Innenstab [1]
        # Nummer des Innenstabs [2]
        
        if item1 not in self.list_aussenstab:
            self.list_aussenstab.append(item1)
        if item2 not in self.list_innenstab:    
            self.list_innenstab.append(item2)


        _temp = str("Aussenstab")
        self.item_marker[item1][0] = _temp

        _counter = self.item_marker[item2-1][2]  # take counter value from item before item2 !!!
        if _counter:
            _counter += 1
        else:
            _counter = 1
        _temp = str("v"+str(_counter)+"_Innenstab("+str(item1)+")")
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

    def test_mainloop(self):
        result = []

        # Step1: check direction, and classify items
        for item in range(len(self.db)):
            if item == 0:
                    self.main_direction[item] = []
                    self.subdirection[item] = []
                    self.item_marker[item] = [[],[],[]]
            else:
                #Step1.1 check if the list aussenstab already exists and check item for innenstab
                if self.list_aussenstab:
                    self.check_list_aussenstab(item)
                    
                #Step1.2 mark the relevant items if true


                #Step1.3 check if Innenstab and if true attach item to list
                result = self.check_direction(self.db[item-1], self.db[item])
                result2 = self.check_innenstab(result)
                
                #Step1.4 mark the relevant items if true
                if result2:
                    self.mark_items(item-1, item)
                else:   # fix for wrong markings bei verschachtelten innenstaeben 
                    _counter = self.item_marker[item][2]
                    if _counter:
                        #print('________________________try to apply fix for _counter:', self.item_marker[item])
                        self.item_marker[item][1] = self.item_marker[item-1][1]    # get string from Innenstab before this one
                        #print('________________________fix executed:', self.item_marker[item])


                self.main_direction[item] = result
                #print('==>',item, ' direction:',self.main_direction[item],' subdirection:', self.subdirection[item],' item_marker:', self.item_marker[item])


            
############
if __name__ == "__main__":
    datensammlung = Database()
    horst = Test(datensammlung.stock_data)


