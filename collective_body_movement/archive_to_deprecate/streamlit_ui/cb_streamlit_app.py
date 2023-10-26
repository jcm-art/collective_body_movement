

import random

import altair as alt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


from collective_body_movement.datamanager.data_manager import CollectiveBodyDataManager


class CollectiveBodyStreamlitApp:

    MAX_DATASETS = 2

    def __init__(self) -> None:

        # Establish page configuration
        self._set_page_configuration()

        # Load datasets and metrics
        self.cbdm = self.fetch_database_for_application(
            database_directory="data/movement_database/", 
            metrics_directory="data/movement_database/")

        # Request user input for number of datasets to load
        # TODO (jcm-art): Determine whether to update dynamically or to prepopulate and hide
        self.num_datasets = 1
        self._request_dataset_parameters()
        self._add_dataset_visualizations(self.num_datasets)
    
    def _set_page_configuration(self):
        # Streamlit page configuration and formatting
        st.set_page_config(layout="wide") # Removing this narrows to ~1/2 of screen
        st.title("Colletive Body Movement")

        # Define an expander at the top to provide more information for the app
        with st.expander("About this app"):
            st.write('This app allows the user to view and analyze movement logs from actors in the Collective Body work. For more information, visit https://www.sarahsilverblatt.com/about')

    def _add_request_num_dataset(self):

        st.header("How many datasets do you want to compare today?")
        self.number_dataset = st.selectbox(
            label="Select a dataset ID",
            options=[1,2],
        )

    def _request_dataset_parameters(self):
        '''
        Request user input for parameters of datasets to load
        '''

        self._initialize_dataset_parameters()
        
        # Loop through number of datasets
        i = 0


        # TODO (jcm-art): Implement multiple selections with column layout
        # Select Dataset,  Participant ID, and Metric for visualization
        st.header("Select a Dataset and Paricipant ID")
        self.user_dataset_selections = 0
        self.user_dataset_selections = st.selectbox(
            label="Select a dataset ID",
            options=self.dataset_options,
            key=f"dataset_selection_{i}",
            on_change=self._update_headset_options(i),
        )

        self.user_chapter_selections = st.selectbox(
            label="Select a chapter # (1-3)",
            options=self.chapter_options,
            key=f"chapter_selection_{i}",
        )

        self.user_headset_selections = st.selectbox(
            label="Select a participant ID",
            options=self.headset_options[i],
            key=f"headset_selection_{i}",
        )

        # TODO (jcm-art): Break out metric selection to be common across all
        # TODO (jcm-art): Potential to add multiple metrics per dataset
        metric_options = self.cbdm.get_metric_options()
        self.user_metric_selections = st.selectbox(
            label="Select a Metric",
            options=metric_options,
            key=f"metric_selection_{i}",
        )

    def _update_headset_options(self,i):
        self.headset_options[i] = self.cbdm.get_actor_IDs(self.user_dataset_selections)

    def _add_dataset_visualizations(self, num_datasets):
        
        # Define parameter for loop
        i = 1

        self._create_figure(self.user_dataset_selections, self.user_headset_selections,  self.user_chapter_selections, self.user_metric_selections)


    def _create_figure(self, dataset_selection, headset_selection, chapter_selection, metric_selection):

        movement_data_dictionary = self.cbdm.get_frame_dataset_dict(dataset_selection, headset_selection, chapter_selection, normalize=True)
        chapter_df = movement_data_dictionary["dataset"]

        x = chapter_df["head_pos_x"].tolist()
        y = chapter_df["head_pos_z"].tolist()
        step=2
        xx = x[0:-1:step]
        yy = y[0:-1:step]
        N = len(xx)

        fig = go.Figure(
            data=[
                go.Scatter(
                    x=x, 
                    y=y, 
                    mode="lines",
                    line=dict(width=1, color="white", dash='dot')),
                go.Scatter(
                    x=x, 
                    y=y, 
                    mode="lines",
                    line=dict(width=1, color="white", dash='dot'))],
                layout=go.Layout(
                    xaxis=dict(range=[0,1], autorange=False, zeroline=False),
                    yaxis=dict(range=[0,1], autorange=False, zeroline=False),
                    title_text="Actor Position", hovermode="closest",
                    updatemenus=[dict(type="buttons",
                                    buttons=[dict(label="Play",
                                                    method="animate",
                                                    args=[
                                                        None, {"frame": {"duration": 15, "redraw": False},
                                                            "fromcurrent": True, 
                                                            "transition": {"duration": 10,"easing": "quadratic-in-out"}}],
                                                    )])]),
                frames=[go.Frame(
                    data=[go.Scatter(
                        x=[xx[k]],
                        y=[yy[k]],
                        mode="markers",
                        marker=dict(color="red", size=10))])
                        
                    for k in range(N)]
        )
        # TODO - add a slider (requires pregenerated frames)
        # https://plotly.com/python/sliders/

        st.write(fig)

    # TODO (jcm-art): Migrate to form to reduce reloading or deprecate
    def _dataset_request_form(self):
        st.header("Dataset Visualiation Options")
        st.subheader('Coffee machine')

        with st.form('my_form'):
            st.subheader('**Choose dataset parameters**')

            # Input widgets
            coffee_bean_val = st.selectbox('Coffee bean', ['Arabica', 'Robusta'])
            coffee_roast_val = st.selectbox('Coffee roast', ['Light', 'Medium', 'Dark'])
            brewing_val = st.selectbox('Brewing method', ['Aeropress', 'Drip', 'French press', 'Moka pot', 'Siphon'])
            serving_type_val = st.selectbox('Serving format', ['Hot', 'Iced', 'Frappe'])
            milk_val = st.select_slider('Milk intensity', ['None', 'Low', 'Medium', 'High'])
            owncup_val = st.checkbox('Bring own cup')

            # Every form must haved a submit button
            submitted = st.form_submit_button('Submit')

    @st.cache_resource
    def fetch_database_for_application(_self, database_directory, metrics_directory):
        '''
        Funtion to load datasets and metrics.
        '''
        cbdm = CollectiveBodyDataManager(
            database_directory="data/movement_database/", 
            metrics_directory="data/movement_database/")

        return cbdm

    def _initialize_dataset_parameters(self):
        # Get options from main data manager
        self.dataset_options = self.cbdm.get_session_IDs()
        self.headset_options = [range(1,6) for x in range(self.MAX_DATASETS)]
        self.chapter_options = range(1,4)
        self.metric_options = self.cbdm.get_metric_options()
        print(self.metric_options)

    def run_streamlit(self):
        pass



if __name__=="__main__":
    cb_streamlit_app = CollectiveBodyStreamlitApp()
