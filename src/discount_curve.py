# -*- coding: utf-8 -*-
"""
Created on Sun Nov 14 02:44:43 2021

@author: пользователь
"""
import numpy as np
import pandas as pd
from interpolation import Interpolator

class DiscountCurve:
    
    def __init__(self, dt: np.ndarray):
        
        dt = pd.DataFrame(dt, columns = ['instrument', 'index', 'StartDate', 'EndDate'])
        
        dt['StartDate'] = pd.to_datetime(dt['StartDate'], format='%m/%d/%y')
        dt['EndDate'] = pd.to_datetime(dt['EndDate'], format='%m/%d/%y')
        dt['rate'] = dt['index']
        dt.loc[dt['instrument']!='Libor3m', 'rate'] = (100-dt['rate'])*0.01
        
        res = pd.DataFrame({'date': pd.date_range(dt['StartDate'].min(), dt['EndDate'].max())})
        res = res.merge(dt[['EndDate', 'rate']].rename(columns={'EndDate': 'date'}), how = 'left', on = 'date') 
        res = res.merge(dt[['StartDate', 'rate']].rename(columns={'StartDate': 'date_prev'}), how = 'left', on = 'rate')
        res['date_prev'] = res['date_prev'].fillna(method = 'bfill').shift(1).fillna(method = 'ffill')
        res.index = res['date']
        res['discount_factor'] = 1/(1+res['rate']*(res['date']-res['date_prev']).dt.days/360)
        
        res.loc[res['date']==res['date'].min(), 'discount_factor'] = 1
        res['x'] = (res['date']-res['date'].min()).dt.days
        
        x = res.loc[~res['discount_factor'].isna()]['x'].to_list()
        y = res.loc[~res['discount_factor'].isna()]['discount_factor'].to_list()
        
        df = [Interpolator.interpolate(x, y, i) for i in res['x'].to_list()]
        
        res['discount_factor'] = df
        
        
        self.curve = res['discount_factor'].to_dict()
        
    def get(self, date: None):
        if isinstance(date, str):
            return self.__dict__['curve'].get(pd.to_datetime(date))
        elif isinstance(date, list):
            return [self.__dict__['curve'].get(pd.to_datetime(d)) for d in date]
        else:
            print('Input argument not string or list')   
        
        
        
import unittest
import numpy as np

class Test(unittest.TestCase):
    """Testing of z range and correct output values of LinearInterpolation class"""
        
    def test_values(self):
        """Output Values"""
        dt = pd.read_csv('../data/USD rates.csv')
        curve = DiscountCurve(pd.DataFrame(dt.drop('Conv, adj', axis = 1).to_numpy(), columns = ['instrument', 'index', 'StartDate', 'EndDate']))
        
        self.assertEqual(curve.get('2021-10-29'), 0.9999964039678646)
        
if __name__ == '__main__':
    unittest.main()
        
        
