

import numpy as np
    

class ColorManipulator:

    def __init__(self) -> None:
        pass

    def color_to_rgb(self, color):
        return tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_color(self, rgb_tuple):
        return f'#%02x%02x%02x' % rgb_tuple

    def interpolate_colors(self, min_val, max_val, min_color, last_color, metric_val):
        min_rgb = self.color_to_rgb(min_color)
        last_rgb = self.color_to_rgb(last_color)
        rgb_range = [int(min_rgb[i] + (last_rgb[i]-min_rgb[i])*metric_val/(max_val-min_val)) for i in range(3)]
        return self.rgb_to_color(tuple(rgb_range))
    
    def get_color_array(self, first_color: str, second_color:str, x):

        color_array = []
        x_min = np.min(x)
        x_max = np.max(x) if  np.max(x)-x_min > 1e-4 else x_min+1.0

        for datapoint in x:
            datapoint_color = self.interpolate_colors(x_min, x_max, first_color, second_color, datapoint)
            color_array.append(datapoint_color)

        return color_array