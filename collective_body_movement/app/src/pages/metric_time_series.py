# Collective Body Movement Application
# Director: Sarah Silverblatt-Buser (https://www.sarahsilverblatt.com/)
# Author: Justin Martin (jcm-art)

import json
import platform
import time
from typing import Dict, List

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from ..utils import StreamlitPage, AppProfiler
from ..data_management.movement_data import MovementDataManager
from ..data_management.movement_frame import UserMetricFrame


class MetricSeriesPage(StreamlitPage):

    def __init__(self, state):
        print("Initializing MetricSeriesPage")
        self.state = state
        self.profiler = AppProfiler(True)

        # Create data manager
        self.profiler.start_timer()
        self._create_data_manager()
        self.profiler.end_timer("Data manager creation")

    def write(self):
        st.title("Collective Body Metric Time Series")

        # Make expander
        self.profiler.start_timer()
        self._make_expander()

        # Make sidebar
        self._make_sidebar()

        # Get uploaded files
        self.mdm.load_movement_data_from_upload()

        # Request user metric parameters
        self._request_user_metric_parameters()
        self.profiler.end_timer("Sidebar, expander, user input creation")

        # Get movement dataframe for metrics
        self.movement_df = self.mdm.get_updated_dataframe(self.user_dataset_selection, self.user_chapter_selection_static)
        self.available_columns = self.movement_df.columns
        print(f"Grabbed a new data frame with {self.user_dataset_selection}, {self.user_chapter_selection_static}")

        # Make Metric Time Series 
        self.display_selected_columns = st.multiselect(
            label="Select what metrics to explore.",
            options=self.available_columns,
            default=self.available_columns[0]
        )

        self._plot_time_series(self.display_selected_columns)


    def _plot_time_series(self, time_series_values: List[str]):

        for column in time_series_values:
            time_series_data = []

            tmp_scatter = go.Scatter(
                x=self.movement_df['timestamp'], y=self.movement_df[column],name=f"{column}"
            )

            time_series_data.append(tmp_scatter)

            time_series_layout = go.Layout(
                title=f'Time Series plot for for {column} ',
                barmode='overlay',
                xaxis=dict(
                    title='timestamp'
                ),
                yaxis=dict(
                    title=f"Dataset {column} Column"
                ),
            )

            time_series_fig = go.Figure(data=time_series_data, layout = time_series_layout)
            
            # Plot time series
            st.write(time_series_fig)



    def _create_data_manager(self):
        self.mdm = MovementDataManager()

        # Attempt local file upload
        try:
            data_filepath = "../data/new_pipeline/6_normalized_output/CollectiveBodyBolt_output"
            self.mdm.load_local_movement_data_from_filepath(data_filepath)
        except:
            print("Local filepath unavailable")

    def _make_expander(self):
        # Define an expander at the top to provide more information for the app
        with st.expander("About this app"):
            st.write('This app allows the user to view and analyze movement logs from actors in the Collective Body work. For more information, visit https://www.sarahsilverblatt.com/about')

    def _make_sidebar(self):
        st.sidebar.header("Input")
        self.speed = st.sidebar.selectbox("Speed", options=["Slow", "Normal", "Fast"], index=1)


    def _request_user_metric_parameters(self):
        st.header("Select a Dataset and Participant ID")
        dataset_options = self.mdm.get_dataset_IDs()
        # TODO (jcm-art): update options for participant ID based on dataset selection
        self.user_dataset_selection = st.selectbox(
            label="Select a dataset ID",
            options=dataset_options,
        )

        #headset_options = self.mdm.get_actor_IDs(self.user_dataset_selection)
        #self.user_headset_selection = st.selectbox(
        #    label="Select a participant ID",
        #    options=headset_options,
        #)

        # TODO - add option for all
        chapter_options = [1,2,3]
        self.user_chapter_selection_static = st.selectbox("Select a chapter?", chapter_options,index=0)