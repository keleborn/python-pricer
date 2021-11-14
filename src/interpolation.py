class Interpolator:
    """Linear interpolator.
    """

    @staticmethod
    def interpolate(x_list: list, y_list: list, z: float):
        """Linear interpolate.
        Parameters
        __________
        x_list : list
            x values.
        y_list: list
            y values.
        z: float
            Interpolate in that point z.
        Returns
        _______
        float
            Interpolate value.
        Raises
        ______
        ValueError
            x_list must be sorted ASC.
        """
        if x_list != sorted(x_list):
            raise ValueError('x_list must be sorted ASC')
        for index, element in enumerate(x_list):
            if z <= element:
                delta = (z - x_list[index - 1]) / (x_list[index] - x_list[index - 1])
                answer = y_list[index - 1] + (y_list[index] - y_list[index - 1]) * delta
                break
        return answer

