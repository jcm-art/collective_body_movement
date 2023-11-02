import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.figure_factory as ff

import numpy as np
import pandas as pd
import streamlit as st

from typing import Tuple

from datamanager.data_manager import CollectiveBodyDataManager


# Streamlit page configuration and formatting
st.set_page_config(layout="wide") # Removing this narrows to ~1/2 of screen
st.title("Animation scratchpad")




# https://discuss.streamlit.io/t/how-to-prevent-st-upload-from-rerunning-after-uploading-file/37402/2


# Load datasets and metrics

# TODO (jcm-art): Prevent database reload with every page option selection
@st.cache_resource
def fetch_database_for_application(database_directory, metrics_directory):
    cbdm = CollectiveBodyDataManager(
        database_directory=database_directory, 
        metrics_directory=metrics_directory)
    return cbdm

@st.cache_resource
def set_uploaded_data(metrics_file, movement_file, metrics_json):
    cbdm = CollectiveBodyDataManager(
        raw_movement_df=pd.read_csv(movement_file),
        algorithm_metrics_df=pd.read_csv(metrics_file),
        metrics_json=metrics_json
    )
    return cbdm

# cbdm = fetch_database_for_application("../data/movement_database/", "../data/movement_database/")

def run_streamlit_app():

    cbdm = set_uploaded_data(metrics_file, movement_file, metrics_json)

    # Select Dataset,  Participant ID, and Metric for visualization
    st.header("Select a Dataset and Paricipant ID")
    dataset_options = cbdm.get_session_IDs()
    # TODO (jcm-art): update options for participant ID based on dataset selection
    user_dataset_selection = st.selectbox(
        label="Select a dataset ID",
        options=dataset_options,
    )

    headset_options = cbdm.get_actor_IDs(user_dataset_selection)
    user_headset_selection = st.selectbox(
        label="Select a participant ID",
        options=headset_options,
    )

    metric_options = cbdm.get_metric_options()
    user_metric_selection = st.selectbox(
        label="Select a Metric",
        options=metric_options,
    )

    chapter_options = [1,2,3]
    user_chapter_selection_static = st.selectbox("Select a chapter?", chapter_options,index=0)

    st.sidebar.header("Input")
    speed = st.sidebar.selectbox("Speed", options=["Slow", "Normal", "Fast"], index=1)

    # Plot the selected dataset

    # TODO - add frames to skip and duration as metaparameters for animation

    st.header("Data plots")

    st.subheader("Static Movement Chart")

    movement_data_dictionary = cbdm.get_frame_dataset_dict(user_dataset_selection, user_headset_selection, chapter_num=user_chapter_selection_static, normalize=True)
    movement_df = movement_data_dictionary["dataset"]
    chapter_df = movement_df[movement_df["chapitre"] == user_chapter_selection_static]

    x = chapter_df["head_pos_x"].tolist()
    y = chapter_df["head_pos_z"].tolist()
    len_x = len(x)
    if speed == "Slow":
        frames_to_skip = 1
        duration = 50
    elif speed == "Normal":
        frames_to_skip = 1
        duration = 10
    elif speed == "Fast":
        frames_to_skip = 1
        duration = 0


    step_nums = [str(i) for i in range(0,len_x)]

    # make figure
    fig_dict = {
        "data": [],
        "layout": {},
        "frames": []
    }

    # fill in most of layout
    fig_dict["layout"]["xaxis"] = {
        "range": [-.01, 1.01], 
        "title": "xaxis",
        "autorange": False,
        #"showticklabels": False,
        "showgrid": False,
        "zeroline": False,
    }
    fig_dict["layout"]["width"] = 600
    fig_dict["layout"]["height"] = 600
    fig_dict["layout"]["yaxis"] = {"range": [-.01, 1.01], "title": "yaxis"}
    fig_dict["layout"]["hovermode"] = "closest"
    fig_dict["layout"]["updatemenus"] = [
        {
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": duration, "redraw": False},
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

    sliders_dict = {
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

    # make data
    data_dict = {
        "x": x,
        "y": y,
        "mode": "lines",
        "line": {
            "width": 2
        },
        "name": "All Data"
    }
    fig_dict["data"].append(data_dict)

    data_dict_2 = {
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
    fig_dict["data"].append(data_dict_2)


    trailing_arrows = 1

    # make frames
    @st.cache_data
    def make_frames():
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


    fig_dict["layout"]["sliders"] = [make_frames()]

    fig = go.Figure(fig_dict)

    st.write(fig)

    first_color = st.color_picker('Pick the first Color', '#00f900')

    second_color = st.color_picker('Pick the second Color', '#00f900')

    colorscale_data = np.arange(256).repeat(256).reshape(256,256).T/256

    #fig = px.imshow(colorscale_data, color_continuous_scale=[first_color, second_color])
    #fig.update_xaxes(visible=False)
    #fig.update_yaxes(visible=False)

    #st.write(fig)

    dataset_id = movement_df["dataset_id"].unique()[0]

    metrics_fig = make_subplots(rows=1, cols=1)
    im_for_fig = px.imshow(colorscale_data)

    all_metrics = cbdm.get_chosen_metric(user_metric_selection)
    dataset_metric = all_metrics[all_metrics["data_collect_name"] == dataset_id][user_metric_selection].values[0]
    metric_array = all_metrics[user_metric_selection].to_numpy()


    def color_to_rgb(color):
        return tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_color(rgb_tuple):
        return f'#%02x%02x%02x' % rgb_tuple

    def interpolate_colors(min_val, max_val, min_color, last_color, metric_val):
        min_rgb = color_to_rgb(min_color)
        last_rgb = color_to_rgb(last_color)
        rgb_range = [int(min_rgb[i] + (last_rgb[i]-min_rgb[i])*metric_val/(max_val-min_val)) for i in range(3)]
        return rgb_to_color(tuple(rgb_range))

    metric_color = interpolate_colors(metric_array.min(), metric_array.max(), first_color, second_color, dataset_metric)

    html_string = f"<p style=\"color:{metric_color}\">This is the user's metric color.</p>"
    st.markdown(html_string, unsafe_allow_html=True)

    metrics_fig.add_trace(
        go.Histogram(x=all_metrics[user_metric_selection]),
        row=1, col=1)
    metrics_fig.add_trace(
        go.Scatter(x=[dataset_metric], y=[0], mode="markers", marker=dict(color=metric_color, size=10)),
        row=1, col=1
    )
    # TODO - add custom color heatmap Custom Heatmap Color scale with Graph Objects https://plotly.com/python/colorscales/

    color_df = all_metrics
    color_df["fake_y"]=0

    color_scale_fig = px.scatter(color_df, x=user_metric_selection, y="fake_y", color=user_metric_selection,color_continuous_scale=[first_color, second_color])
    st.plotly_chart(color_scale_fig)
    max_metric = metric_array.max()
    min_metric = metric_array.min()
    st.plotly_chart(metrics_fig)

    #color_array =[first_color*metric/(max_metric-min_metric)+second_color*(max_metric-metric)/(max_metric-min_metric) for metric in metric_array]


    # colors = [interpolate_colors(min_metric, max_metric, first_color, second_color, metric) for metric in metric_array]
    #dist_fig = ff.create_distplot([metric_array], ['distplot'], colors=colors)
    #st.plotly_chart(dist_fig)



# Define an expander at the top to provide more information for the app
with st.expander("About this app"):
    st.write('This app allows the user to view and analyze movement logs from actors in the Collective Body work. For more information, visit https://www.sarahsilverblatt.com/about')

metrics_file = st.file_uploader("Upload metrics file", type=["csv"])
movement_file = st.file_uploader("Upload raw data movement file", type=["csv"])
metrics_json = st.file_uploader("Upload metrics json file", type=["json"])

run_streamlit_app()