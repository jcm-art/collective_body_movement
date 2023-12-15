# Collective Body Movement Application
# Director: Sarah Silverblatt-Buser (https://www.sarahsilverblatt.com/)
# Author: Justin Martin (jcm-art)

import json

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from ..data_management.color import ColorManipulator
from ..utils import StreamlitPage


class MetricsSummaryPage(StreamlitPage):

    def __init__(self, state):
        self.state = state

        self.metrics_type_dict = {
            "Basic": "all_basic_data_metrics", 
            "Algorithms": "all_metrics",
        }

        self.color_manipulator = ColorManipulator()

    def write(self):
        st.title("Collective Body Metrics Summary")

        st.header("Metrics Summary")

        metrics = self._get_metrics_file()
        algorithm_selection, \
            metric_selections = self._display_selections(metrics)
        
        self._plot_selections(metrics, algorithm_selection, metric_selections)

    def _get_metrics_file(self):
        metrics_file = st.file_uploader("Upload metrics file", type=["json"])
        metrics_file = json.load(metrics_file)
        metrics_file = {
            "all_metrics": metrics_file["normalized_algorithm_metrics"],
            "all_basic_data_metrics": metrics_file["normalized_basic_metrics"]
        }
        # st.json(metrics_file)
        return metrics_file

    def _display_selections(self, metrics):
        st.subheader("Select an Algorithm and Metric to Explore")
        metric_type_options = list(self.metrics_type_dict.keys())
        metric_type_selections = st.multiselect(
            label="Explore Basic Metrics or Algorithms?",
            options=metric_type_options,
            default=metric_type_options[1]
        )

        # TODO - select and compare multiple algorithms
        algorithm_options = []
        for metric_type_selection in metric_type_selections:
            translated_key = self.metrics_type_dict[metric_type_selection]
            algorithm_options += list(metrics[translated_key].keys())

        algorithm_selections = st.multiselect(
            label="Select algorithms",
            options=algorithm_options,
            default=algorithm_options[0]
            
        )

        metric_options = []
        for key in self.metrics_type_dict.values():
            for algorithm_selection in algorithm_selections:
                if algorithm_selection in metrics[key]:
                    metric_options = metric_options+list(metrics[key][algorithm_selection].keys())[1:]
        
        metric_selections = st.multiselect(
            label="Select what metrics to explore.",
            options=metric_options,
            default=metric_options[0]
        )

        self.first_color = st.color_picker('Pick the first Color', '#8C00F9')
        self.second_color = st.color_picker('Pick the second Color', '#FFCE00')


        return algorithm_selections, metric_selections
    
    def _plot_selections(self, metrics, algorithm_selections, metric_selections):
        print(f"Updating plot with {metric_selections} for algorithm {algorithm_selections}")

        hist_data = []
        prob_data = []

        for key in self.metrics_type_dict.values():
            for algorithm_selection in algorithm_selections:
                if algorithm_selection in metrics[key]:
                    for metric in metric_selections:
                        if metric in metrics[key][algorithm_selection]:
                            print("hello")
                            # Build Histogram Data
                            x = metrics[key][algorithm_selection][metric]

                            # Build cummulative distribution chart
                            rank = np.arange(0,len(x))
                            x = np.sort(x)

                            # Get colors for cummulative dist chart
                            
                            colors = self.color_manipulator.get_color_array(self.first_color, self.second_color, x)
                            
                            tmp_hist = go.Histogram(
                                x=x,name=f"{metric}_{algorithm_selection}"
                            )

                            #num_bins = tmp_hist.xaxis 
                            #st.write(f"xaxis is {num_bins}")
                            # TODO (jcm-art): Fix histogram colors
                            hist_colors = np.arange(0.0,1.1,0.1)
                            marker={
                                    'color': hist_colors,
                                    'cmin': 0.0,
                                    'cmax': 1.0,
                                    'colorscale': [[0, self.first_color], [1, self.second_color]]
                                }
                            #tmp_hist.marker = marker
                            hist_data.append(tmp_hist)

                            prob_data.append(
                                go.Scatter(
                                    x=rank, y=x, name=f"{metric}_{algorithm_selection}",
                                    mode="markers", marker={
                                        "color": colors, 
                                        "size":5
                                    }
                                ))

        # Build layout and cummulative distribution layout
        hist_layout = go.Layout(
                title=f'Histogram of Metrics for {algorithm_selections} ',
                barmode='overlay',
                xaxis=dict(
                title='Distribution'
                ),
                yaxis=dict(
                    title=f"Bin Count for {metric_selections} Metrics"
                ),
            ) 

        prob_layout = go.Layout(
                title=f'Cummulative Probability Distribution of Metrics for {algorithm_selections} ',
                barmode='overlay',
                xaxis=dict(
                    title='Rank in Dataset (ascending)'
                ),
                yaxis=dict(
                    title=f"Score in Dataset {metric_selections} Metric"
                ),
            ) 

        hist_fig = go.Figure(data=hist_data, layout=hist_layout)
        st.write(hist_fig)
    
        prob_fig = go.Figure(data=prob_data, layout=prob_layout)
        st.write(prob_fig)