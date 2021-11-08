from src.interpolation import Interpolator


def test_correct_work():
    i = Interpolator()
    assert i.interpolate(x_list=[0, 1, 2, 3, 5], y_list=[0, 1, 4, 9, 25], z=2.5) == 6.5
