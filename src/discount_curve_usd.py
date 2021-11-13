from src.interpolation import Interpolator
import numpy as np
import pandas as pd
import re
import datetime


class DiscountingCurveUSD:
    """
    Class for constructing USD Discounting Curve
    """

    @staticmethod
    def get_discount_curve_usd(initial_date: datetime.datetime, required_end_dates: list, verbose=False):
        """
        Construct USD Discounting Curve using ON Fed rate, LIBOR USD 3M and Eurodollar futures
        :param initial_date: start date to which we discount
        :param required_end_dates: list of different end dates from which we discount
        :param verbose: boolean parameter indicating whether program shows output results (prints/plots)
        :return: 2-dimensional list with required end dates and corresponding discount factors [[date_i; df_i];...]
        """

        def get_sorted_data():
            """
            Processing given data with ON Fed rate, LIBOR USD 3M and Eurodollar futures
            :return: 3-dimensional list [[days to start of the given rate (from initial date);
                                          length of the period in days;
                                          quoted rate for the period];...]
            """
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
                if re.match(row_ed_futures + "[HMUZ][0-9]", term):  # matching eurodollar futures
                    ir_days_to_start.append((start_date - initial_date).days)
                    ir_length.append((end_date - start_date).days)
                    ir_rates.append((100 - price) / 100)
                elif term in [row_overnight, row_libor3m]:  # matching overnight rate or LIBOR 3M
                    ir_days_to_start.append((start_date - initial_date).days)
                    ir_length.append((end_date - start_date).days)
                    ir_rates.append(price)
                else:
                    print("{:} object has not been recognized!".format(term))

            mix_sorted = sorted(zip(ir_days_to_start, ir_length, ir_rates))
            return mix_sorted

        # Creating lists for storing zero rates from the initial date to every required end date
        # Necessary for incremental bootstrapping the other zero rates and calculating discount factors
        # Rates are stored as simple rates for the specified period N' = N * (1 + R * time)
        usd_zero_rates_days = []
        usd_zero_rates_values = []

        # Function bootstraps zero curve for every new period one by one
        def add_new_rate_to_zero_curve(days_to_start, length, internal_rate):
            if days_to_start == 0:
                usd_zero_rates_days.append(length)
                usd_zero_rates_values.append(internal_rate)
                return

            # If a new period overlaps (doesn't touch) the calculated period then we use interpolation (extrapolation)
            # We are using linear interpolation and flat extrapolation here
            rate1 = Interpolator.interpolate(usd_zero_rates_days, usd_zero_rates_values, days_to_start)
            rate2 = internal_rate
            # Now we can simply calculate rate for period [t0, t2] given rates for [t0, t1] and [t1, t2] periods
            # DCF is assumed to be act/360
            total_rate = ((1 + rate1 * days_to_start / 360) * (1 + rate2 * length / 360) - 1) / \
                         ((days_to_start + length) / 360)
            usd_zero_rates_days.append(days_to_start + length)
            usd_zero_rates_values.append(total_rate)

        # Function calculates discount factor for zero rate over the given period
        def get_discount_factor(days, rate):
            return (rate * days / 360 + 1) ** (-1)

        # Retrieving given market data
        mix_sorted = get_sorted_data()
        # Bootstrap zero curve for every period from the given data
        for days_to_start, length, rate in mix_sorted:
            add_new_rate_to_zero_curve(days_to_start, length, rate)

        # Constructing zero and discounting curves
        zero_curve_usd = []
        discount_curve_usd = []
        for end_date in required_end_dates:
            days = (end_date - initial_date).days
            # Interpolating rate for every required end date from our bootstrapped zero curve
            interpolated_rate = Interpolator.interpolate(usd_zero_rates_days, usd_zero_rates_values, days)
            df = get_discount_factor(days, interpolated_rate)
            if verbose:
                print("Interpolated rate for {:} days: {:.4f}%".format(days, interpolated_rate * 100))
                print("Discount factor for {:} days: {:.6f}".format(days, df))
            zero_curve_usd.append(interpolated_rate)
            discount_curve_usd.append(df)

        # Show resulting plots if verbose flag is True
        if verbose:
            from matplotlib.dates import (MONTHLY, DateFormatter,
                                          rrulewrapper, RRuleLocator)
            from matplotlib.ticker import FuncFormatter
            import matplotlib.pyplot as plt

            rule = rrulewrapper(MONTHLY, interval=6)
            loc = RRuleLocator(rule)
            formatter = DateFormatter('%m/%d/%y')
            fig, ax = plt.subplots()
            plt.plot(required_end_dates, np.array(zero_curve_usd) * 100)
            ax.xaxis.set_major_locator(loc)
            ax.xaxis.set_major_formatter(formatter)
            ax.xaxis.set_tick_params(labelsize=10)
            ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: '{:.2f}%'.format(x)))
            plt.xticks(rotation=30)
            plt.title("USD zero simple rate curve")
            plt.show()

            fig, ax = plt.subplots()
            plt.plot(required_end_dates, discount_curve_usd)
            ax.xaxis.set_major_locator(loc)
            ax.xaxis.set_major_formatter(formatter)
            ax.xaxis.set_tick_params(labelsize=10)
            plt.xticks(rotation=30)
            plt.title("USD discounting curve")
            plt.show()

        return list(zip(required_end_dates, discount_curve_usd))
