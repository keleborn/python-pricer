import sys
sys.path.insert(0, '../src')

from interpolation import Interpolator
from discount_curve import DiscountCurve

import unittest
import pandas as pd


class Test(unittest.TestCase):
    def test_correct_work(self):
        i = Interpolator()
        self.assertEqual(i.interpolate(x_list=[0, 1, 2, 3, 5], y_list=[0, 1, 4, 9, 25], z=2.5), 6.5)
        """Testing of z range and correct output values of LinearInterpolation class"""
        
    def test_df(self):
        """Output Values"""
        dt = pd.read_csv('../data/USD rates.csv')
        curve = DiscountCurve(pd.DataFrame(dt.drop('Conv, adj', axis = 1).to_numpy(), columns = ['instrument', 'index', 'StartDate', 'EndDate']))
        
        self.assertEqual(curve.get('2021-10-29'), 0.9999964039678646)
        
if __name__ == '__main__':
    unittest.main()
        