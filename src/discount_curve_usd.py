from src.interpolation import Interpolator
import numpy as np
import pandas as pd
import re
import datetime

# x = list(np.linspace(-10, 20, 50))
# print(Interpolator.interpolate(x, np.sin(x), -10))


class DiscountingCurveUSD:
    """...
    """

    def __init__(self, initial_date: datetime.datetime):
        """
        Initializing with Eurodollar futures prices + Libor3M + ON Fed rate
        """
        self.data = pd.read_csv("../data/USD rates.csv")
        self.column_term = "Term"
        self.column_price = "Price"
        self.column_start_date = "StartDate"
        self.column_end_date = "EndDate"
        self.row_overnight = "ON"
        self.row_libor3m = "Libor3m"
        self.row_ed_futures = "ED"

        self.initial_date = initial_date

        self.ir_days_to_start = []
        self.ir_length = []
        self.ir_rates = []
        for i, row in self.data.iterrows():
            term = row[self.column_term]
            price = row[self.column_price]
            start_date = datetime.datetime.strptime(row[self.column_start_date], "%m/%d/%y")
            end_date = datetime.datetime.strptime(row[self.column_end_date], "%m/%d/%y")
            if re.match("ED[HMUZ][0-9]", term):
                self.ir_days_to_start.append((start_date - self.initial_date).days)
                self.ir_length.append((end_date - start_date).days)
                self.ir_rates.append((100 - price) / 100)
            elif term in [self.row_overnight, self.row_libor3m]:
                self.ir_days_to_start.append((start_date - self.initial_date).days)
                self.ir_length.append((end_date - start_date).days)
                self.ir_rates.append(price)
            else:
                print("{:} object has not been recognized!".format(term))



    def get_discount_curve_usd(self, required_dates):
        self.usd_zero_rates_days = []
        self.usd_zero_rates_values = []  # TODO: add compounding?

        def add_new_rate_to_(days_to_start, length, internal_rate):
            if days_to_start == 0:
                self.usd_zero_rates_days.append(length)
                self.usd_zero_rates_values.append(internal_rate)
                return

            rate1 = Interpolator.interpolate(self.usd_zero_rates_days, self.usd_zero_rates_values, days_to_start)
            rate2 = internal_rate
            total_rate = ((1 + rate1 * days_to_start / 360) * (1 + rate2 * length / 360) - 1) / \
                         ((days_to_start + length) / 360)
            self.usd_zero_rates_days.append(days_to_start + length)
            self.usd_zero_rates_values.append(total_rate)

        mix_sorted = sorted(zip(self.ir_days_to_start, self.ir_length, self.ir_rates))
        # self.ir_days_to_start, self.ir_length, self.ir_rates = list(zip(*mix_sorted))

        for days_to_start, length, rate in mix_sorted:
            add_new_rate_to_(days_to_start, length, rate)

        def get_discount_factor(days, rate):
            return (days * rate / 360 + 1)**(-1)

        discount_curve_usd = []
        for date in required_dates:
            days = (date - self.initial_date).days
            interpolated_rate = Interpolator.interpolate(self.usd_zero_rates_days, self.usd_zero_rates_values, days)
            df = get_discount_factor(days, interpolated_rate)
            print(days, df)
            discount_curve_usd.append(df)

        return list(zip(required_dates, discount_curve_usd))


ff = DiscountingCurveUSD(datetime.datetime(2021, 10, 28))
x = np.arange(datetime.datetime(2021, 10, 28), datetime.datetime(2026, 10, 28), datetime.timedelta(60)).astype(datetime.datetime)
print(x)
print(ff.get_discount_curve_usd(x))
