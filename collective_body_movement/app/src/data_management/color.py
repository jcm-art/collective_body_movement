

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import streamlit as st


    

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


@st.cache_resource
class MetricsColorScaleManager:

    def __init__(self) -> None:
        
        self.colorscale_data = np.arange(256).repeat(256).reshape(256,256).T/256

        self.metrics_fig = make_subplots(rows=1, cols=1)
        self.im_for_fig = px.imshow(self.colorscale_data)

        self.color_manipulator = ColorManipulator()
        #fig = px.imshow(colorscale_data, color_continuous_scale=[first_color, second_color])
        #fig.update_xaxes(visible=False)
        #fig.update_yaxes(visible=False)

        #st.write(fig)

    @st.cache_data
    def update_color_manager(_self, dataset_id, metric_data, user_metric_selection):

        _self.dataset_id = dataset_id
        _self.metric_data = metric_data
        _self.user_metric_selection = user_metric_selection

        _self.dataset_metric = _self.metric_data[_self.metric_data["data_collect_name"] == dataset_id][user_metric_selection].values[0]
        _self.metric_array = _self.metric_data[_self.user_metric_selection].to_numpy()

    def write(self):
        first_color = st.color_picker('Pick the first Color', '#00f900')
        second_color = st.color_picker('Pick the second Color', '#00f900')

        metric_color = self.color_manipulator.interpolate_colors(
            self.metric_array.min(), 
            self.metric_array.max(), first_color, second_color, 
            self.dataset_metric
        )

        html_string = f"<p style=\"color:{metric_color}\">This is the user's metric color.</p>"
        st.markdown(html_string, unsafe_allow_html=True)

        self.metrics_fig.add_trace(
            go.Histogram(x=self.metric_data[self.user_metric_selection]),
            row=1, col=1)
        self.metrics_fig.add_trace(
            go.Scatter(x=[self.dataset_metric], y=[0], mode="markers", marker=dict(color=metric_color, size=10)),
            row=1, col=1
        )
        # TODO - add custom color heatmap Custom Heatmap Color scale with Graph Objects https://plotly.com/python/colorscales/

        color_df = self.metric_data
        color_df["fake_y"]=0

        color_scale_fig = px.scatter(color_df, x=self.user_metric_selection, y="fake_y", color=self.user_metric_selection,color_continuous_scale=[first_color, second_color])
        st.plotly_chart(color_scale_fig)
        max_metric = self.metric_array.max()
        min_metric = self.metric_array.min()
        st.plotly_chart(self.metrics_fig)
