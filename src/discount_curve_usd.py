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

    @staticmethod
    def get_discount_curve_usd(initial_date: datetime.datetime, required_end_dates: list):

        def get_sorted_data():
            data = pd.read_csv("../data/USD rates.csv")
            column_term = "Term"
            column_price = "Price"
            column_start_date = "StartDate"
            column_end_date = "EndDate"
            row_overnight = "ON"
            row_libor3m = "Libor3m"
            row_ed_futures = "ED"

            ir_days_to_start = []
            ir_length = []
            ir_rates = []

            for i, row in data.iterrows():
                term = row[column_term]
                price = row[column_price]
                start_date = datetime.datetime.strptime(row[column_start_date], "%m/%d/%y")
                end_date = datetime.datetime.strptime(row[column_end_date], "%m/%d/%y")
                if re.match(row_ed_futures + "[HMUZ][0-9]", term):
                    ir_days_to_start.append((start_date - initial_date).days)
                    ir_length.append((end_date - start_date).days)
                    ir_rates.append((100 - price) / 100)
                elif term in [row_overnight, row_libor3m]:
                    ir_days_to_start.append((start_date - initial_date).days)
                    ir_length.append((end_date - start_date).days)
                    ir_rates.append(price)
                else:
                    print("{:} object has not been recognized!".format(term))

            mix_sorted = sorted(zip(ir_days_to_start, ir_length, ir_rates))
            return mix_sorted


        usd_zero_rates_days = []
        usd_zero_rates_values = []  # TODO: add compounding?

        def add_new_rate_to_(days_to_start, length, internal_rate):
            if days_to_start == 0:
                usd_zero_rates_days.append(length)
                usd_zero_rates_values.append(internal_rate)
                return

            rate1 = Interpolator.interpolate(usd_zero_rates_days, usd_zero_rates_values, days_to_start)
            rate2 = internal_rate
            total_rate = ((1 + rate1 * days_to_start / 360) * (1 + rate2 * length / 360) - 1) / \
                         ((days_to_start + length) / 360)
            usd_zero_rates_days.append(days_to_start + length)
            usd_zero_rates_values.append(total_rate)


        mix_sorted = get_sorted_data()

        for days_to_start, length, rate in mix_sorted:
            add_new_rate_to_(days_to_start, length, rate)

        def get_discount_factor(days, rate):
            return (days * rate / 360 + 1)**(-1)

        discount_curve_usd = []
        for end_date in required_end_dates:
            days = (end_date - initial_date).days
            interpolated_rate = Interpolator.interpolate(usd_zero_rates_days, usd_zero_rates_values, days)
            df = get_discount_factor(days, interpolated_rate)
            print(days, df)
            discount_curve_usd.append(df)

        return list(zip(required_end_dates, discount_curve_usd))


if __name__ == "__main__":
    x = list(np.arange(datetime.datetime(2021, 10, 28), datetime.datetime(2026, 10, 28),
                       datetime.timedelta(60)).astype(datetime.datetime))
    print(DiscountingCurveUSD.get_discount_curve_usd(datetime.datetime(2021, 10, 28), x))
