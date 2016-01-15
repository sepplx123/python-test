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
from EW_testtool_V01 import *

################################       
################################
################################
data = Database()
test = Test(data.stock_data)








#       plots
################################       
################################
################################
style.use('dark_background')

fig = plt.figure()
ax1 = fig.add_subplot(111)
plot1 = candlestick_ohlc(ax1, test.raw_values, width=1.0, colorup='#77d879', colordown='#db3f3f', alpha=1.0)

# plot a new line
#plot2 = ax1.plot(data.dates, data.closes, label='3rd line', color='blue')
plot3 = ax1.plot([0,len(test.raw_values)-1], [0,2000], label='3rd line', color='blue')





for label in ax1.xaxis.get_ticklabels():
    label.set_rotation(90)

#ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y %m %d'))
ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))


#ax1.grid(True)
plt.xlabel('Date')
plt.ylabel('Price')
plt.title("TEST_IMPORT_CSV")
#plt.legend()
plt.subplots_adjust(left=0.11, bottom=0.12, right=0.99, top=0.95, wspace=0.2, hspace=0)
plt.show()
################################       
################################
################################





