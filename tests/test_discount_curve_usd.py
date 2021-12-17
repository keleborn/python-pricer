from src.discount_curve_usd import DiscountingCurveUSD
import datetime
import numpy as np


def test_correct_work(eps=1e-8):
    dates = list(np.arange(datetime.datetime(2021, 10, 29), datetime.datetime(2026, 10, 28),
                           datetime.timedelta(60)).astype(datetime.datetime))
    dates.append(datetime.datetime(2022, 1, 28))
    dates = sorted(list(set(dates)))

    dates_res, usd_df = list(zip(*DiscountingCurveUSD.get_discount_curve_usd(datetime.datetime(2021, 10, 28), dates,
                                                                             verbose=True)))
    dates_res = np.array(dates_res)
    usd_df = np.array(usd_df)

    assert dates == list(dates_res)
    assert np.all(usd_df <= 1.0)
    assert abs(usd_df[dates_res == datetime.datetime(2021, 10, 29)] - (0.0008 * 1 / 360 + 1)**(-1)) < eps

    date1 = datetime.datetime(2021, 10, 28)
    date2 = datetime.datetime(2022, 1, 28)
    assert abs(usd_df[dates_res == date2] - (0.001295 * (date2 - date1).days / 360 + 1)**(-1)) < eps


if __name__ == "__main__":
    test_correct_work()
