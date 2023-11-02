# Collective Body Movement Application
# Director: Sarah Silverblatt-Buser (https://www.sarahsilverblatt.com/)
# Author: Justin Martin (jcm-art)

import json
import platform
import time
from typing import Dict

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from ..utils import StreamlitPage, AppProfiler
from ....datamanager import CollectiveBodyDataManager

class MetricsAnalysisPage(StreamlitPage):

    def __init__(self, state):
        print("Initializing MetricsAnalysisPage")
        self.state = state
        self.profiler = AppProfiler(True)

        # Get platform to enable cloud vs. local loading
        self.platform = platform.processor()

        # Create data manager
        self.profiler.start_timer()
        self._create_data_manager()
        self.profiler.end_timer("Data manager creation")

        # Create color manager
        self.profiler.start_timer()
        self.color_scale_manager = MetricsColorScaleManager()
        self.profiler.end_timer("Color manager creation")



    def write(self):
        st.title("Collective Body Movement Analysis")

        # Make expander
        self.profiler.start_timer()
        self._make_expander()

        # Make sidebar
        self._make_sidebar()

        # Request user metric parameters
        self._request_user_metric_parameters()
        self.profiler.end_timer("Sidebar, expander, user input creation")

        # Create UserMetricFrame
        self.profiler.start_timer()
        self.user_metric_frame = UserMetricFrame(
            self.mdm.cbdm.get_frame_dataset_dict(
                self.user_dataset_selection, 
                self.user_headset_selection, 
                chapter_num=self.user_chapter_selection_static, 
                normalize=True
            ),
            # TODO (jcm-art): remove speed from this call to prevent cacheing per speed
            self.speed,
            self.user_chapter_selection_static, 
        )        
        self.profiler.end_timer("User metric frame creation")

        # Write UserMetricFrame
        self.profiler.start_timer()
        self.user_metric_frame.write()
        self.profiler.end_timer("User metric frame write")

        # Write ColorScaleManager
        # TODO (jcm-art): Manage dataset ID outside of metrics manager
        self.profiler.start_timer()
        self.color_scale_manager.update_color_manager(
            self.user_metric_frame.movement_df["dataset_id"].unique()[0],
            self.mdm.cbdm.get_chosen_metric(self.user_metric_selection),
            self.user_metric_selection)
        
        self.color_scale_manager.write()
        self.profiler.end_timer("Color scale manager update and write")

        self.profiler.write_timing()


    def _create_data_manager(self):
        self.mdm = UserMetricsDataManager()

        if self.platform is not None:
            self.mdm.create_database_from_filepath(
                "../data/movement_database/",
                "../data/movement_database/")
        else:
            self.mdm.create_database_from_upload()

    def _make_expander(self):
        # Define an expander at the top to provide more information for the app
        with st.expander("About this app"):
            st.write('This app allows the user to view and analyze movement logs from actors in the Collective Body work. For more information, visit https://www.sarahsilverblatt.com/about')


    def _make_sidebar(self):
        st.sidebar.header("Input")
        self.speed = st.sidebar.selectbox("Speed", options=["Slow", "Normal", "Fast"], index=1)


    def _request_user_metric_parameters(self):
        st.header("Select a Dataset and Paricipant ID")
        dataset_options = self.mdm.cbdm.get_session_IDs()
        # TODO (jcm-art): update options for participant ID based on dataset selection
        self.user_dataset_selection = st.selectbox(
            label="Select a dataset ID",
            options=dataset_options,
        )

        headset_options = self.mdm.cbdm.get_actor_IDs(self.user_dataset_selection)
        self.user_headset_selection = st.selectbox(
            label="Select a participant ID",
            options=headset_options,
        )

        metric_options = self.mdm.cbdm.get_metric_options()
        self.user_metric_selection = st.selectbox(
            label="Select a Metric",
            options=metric_options,
        )

        chapter_options = [1,2,3]
        self.user_chapter_selection_static = st.selectbox("Select a chapter?", chapter_options,index=0)

@st.cache_resource
class UserMetricFrame:

    def __init__(self, movement_data_dictionary: Dict, speed: str, user_chapter_selection_static) -> None:
        print("Initializing UserMetricFrame")
        self.speed = speed
        self.user_chapter_selection_static = user_chapter_selection_static
        self.movement_data_dictionary = movement_data_dictionary
        self.trailing_arrows = 1


        # Prepare data for frame generation
        self._prepare_data()

        # Make figure
        self._make_figure()



    def _prepare_data(self):
        self.movement_df = self.movement_data_dictionary["dataset"]
        chapter_df = self.movement_df[self.movement_df["chapitre"] == self.user_chapter_selection_static]

        self.x = chapter_df["head_pos_x"].tolist()
        self.y = chapter_df["head_pos_z"].tolist()
        self.len_x = len(self.x)
        if self.speed == "Slow":
            self.frames_to_skip = 1
            self.duration = 50
        elif self.speed == "Normal":
            self.frames_to_skip = 1
            self.duration = 10
        elif self.speed == "Fast":
            self.frames_to_skip = 1
            self.duration = 0

        self.step_nums = [str(i) for i in range(0,self.len_x)]

    def _make_figure(self):
        # make figure
        self.fig_dict = {
            "data": [],
            "layout": {},
            "frames": []
        }

        self._make_layout()
        self._make_animation_menu()
        self.fig_dict["data"].append(self._make_line_data_dict(self.x, self.y))
        self.fig_dict["data"].append(self._make_marker_data_dict(self.x, self.y))

        
        self.fig_dict["layout"]["sliders"] = [
            self.make_frames(
                self.len_x, 
                self.frames_to_skip, 
                self.trailing_arrows, 
                self.step_nums, 
                self.x, 
                self.y, 
                self.fig_dict, 
                self.sliders_dict,
            )
        ]
        self.fig = go.Figure(self.fig_dict)

    def _make_layout(self):
        # fill in most of layout
        self.fig_dict["layout"]["xaxis"] = {
            "range": [-.01, 1.01], 
            "title": "xaxis",
            "autorange": False,
            #"showticklabels": False,
            "showgrid": False,
            "zeroline": False,
        }
        self.fig_dict["layout"]["width"] = 600
        self.fig_dict["layout"]["height"] = 600
        self.fig_dict["layout"]["yaxis"] = {"range": [-.01, 1.01], "title": "yaxis"}
        self.fig_dict["layout"]["hovermode"] = "closest"

    def _make_animation_menu(self):
        self.fig_dict["layout"]["updatemenus"] = [
            {
                "buttons": [
                    {
                        "args": [None, {"frame": {"duration": self.duration, "redraw": False},
                                        "fromcurrent": True, "transition": {"duration": 0,
                                                                            "easing": "quadratic-in-out"}}],
                        "label": "Play",
                        "method": "animate"
                    },
                    {
                        "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                        "mode": "immediate",
                                        "transition": {"duration": 0}}],
                        "label": "Pause",
                        "method": "animate"
                    }
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 87},
                "showactive": False,
                "type": "buttons",
                "x": 0.1,
                "xanchor": "right",
                "y": 0,
                "yanchor": "top"
            }
        ]

        self.sliders_dict = {
            "active": 0,
            "yanchor": "top",
            "xanchor": "left",
            "currentvalue": {
                "font": {"size": 20},
                "prefix": "Frame:",
                "visible": True,
                "xanchor": "right"
            },
            "transition": {"duration": 300, "easing": "cubic-in-out"},
            "pad": {"b": 10, "t": 50},
            "len": 0.9,
            "x": 0.1,
            "y": 0,
            "steps": []
        }

    @st.cache_data
    def _make_line_data_dict(_self, x, y):
        # make data
        line_data_dict = {
            "x": x,
            "y": y,
            "mode": "lines",
            "line": {
                "width": 2
            },
            "name": "All Data"
        }
        return line_data_dict

    @st.cache_data
    def _make_marker_data_dict(_self, x, y):
        marker_data_dict = {
            "x": x,
            "y": y,
            "mode": "markers",
            "marker": {
                "symbol": "arrow",
                "angle": 45,
                "size": 10
            },
            "name": "All Data"
        }
        return marker_data_dict
    
    # make frames
    @st.cache_data
    def make_frames(_self, len_x, frames_to_skip, trailing_arrows, step_nums, x, y, fig_dict, sliders_dict):
        for frame_num in range(0,len_x,frames_to_skip):
            data_dict = {
                "x": x[0:frame_num],
                "y": y[0:frame_num],
                "mode": "lines",
                "line": {
                    "width": 2
                },
                "name": step_nums[frame_num]
            }

            start_num = frame_num - trailing_arrows if frame_num - trailing_arrows > 0 else 0

            data_dict_2 = {
                "x": x[start_num:frame_num],
                "y": y[start_num:frame_num],
                "mode": "markers",
                "marker": {
                    "symbol": "arrow",
                    "angle": 45,
                    "size": 10
                },
                "name": step_nums[frame_num]
            }

            frame = {"data": [], "name": str(frame_num)}

            frame["data"].append(data_dict)
            frame["data"].append(data_dict_2)

            fig_dict["frames"].append(frame)

            slider_step = {"args": [
                [frame_num],
                {"frame": {"duration": 0, "redraw": False},
                "mode": "immediate",
                "transition": {"duration": 0}}
            ],
                "label": frame_num,
                "method": "animate"}
            sliders_dict["steps"].append(slider_step)

        return sliders_dict

    def write(self):
        print("Rewriting metric frame")
        st.write(f"Metric speed is {self.speed}")
        st.write(self.fig)


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
class UserMetricsDataManager:
    def __init__(self) -> None:
        self.cbdm = CollectiveBodyDataManager()

    @st.cache_resource
    def create_database_from_upload(_self):
        # Get Uploaded files
        metrics_file = st.file_uploader("Upload metrics file", type=["csv"])
        movement_file = st.file_uploader("Upload raw data movement file", type=["csv"])
        metrics_json = st.file_uploader("Upload metrics json file", type=["json"])
        
        _self.cbdm.set_data_from_files(
            raw_movement_df=pd.read_csv(movement_file),
            algorithm_metrics_df=pd.read_csv(metrics_file),
            metrics_json=metrics_json
        )
    
    @st.cache_resource
    def create_database_from_filepath(_self, _database_directory, _metrics_directory):
        _self.cbdm.load_data_from_path(
            database_directory=_database_directory, 
            metrics_directory=_metrics_directory
            )
        
    def get_datamanager(self):
        return self.cbdm
    
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

