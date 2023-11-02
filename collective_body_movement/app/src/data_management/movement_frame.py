

from typing import Dict

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

class UserMetricFrame:

    def __init__(self, movement_df: pd.DataFrame, speed: str) -> None:
        print("Initializing UserMetricFrame")
        self.speed = speed
        self.trailing_arrows = 1
        self.movement_df = movement_df

        # Prepare data for frame generation
        self._prepare_data()

        # Make figure
        print("Making a new figure")
        self._make_figure()

    def _prepare_data(self):

        self.x = self.movement_df["head_pos_x"].tolist()
        self.y = self.movement_df["head_pos_z"].tolist()
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
            self._make_frames(
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
        axismin = -1.5
        axismax = 1.5
        window_dimension = 800
        # fill in most of layout
        self.fig_dict["layout"]["xaxis"] = {
            "range": [axismin, axismax], 
            "title": "xaxis",
            "autorange": False,
            #"showticklabels": False,
            "showgrid": False,
            "zeroline": False,
        }
        self.fig_dict["layout"]["width"] = window_dimension
        self.fig_dict["layout"]["height"] = window_dimension
        self.fig_dict["layout"]["yaxis"] = {"range": [axismin, axismax], "title": "yaxis"}
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
    def _make_frames(_self, len_x, frames_to_skip, trailing_arrows, step_nums, x, y, fig_dict, sliders_dict):
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
        st.write(self.movement_df.describe())

