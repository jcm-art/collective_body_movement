# Collective Body Movement Application
# Director: Sarah Silverblatt-Buser (https://www.sarahsilverblatt.com/)
# Author: Justin Martin (jcm-art)

import json

import numpy as np
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import streamlit as st

from ..utils import StreamlitPage


class ClusteringDevelopmentPage(StreamlitPage):

    def __init__(self, state):
        self.state = state

    def write(self):
        st.title("Collective Body Clustering Development")

        # Get and display metric data 
        st.header("Metric Data")
        self.metrics = self._get_metrics_file()
        st.write(self.metrics)

        # Extract metrics for clustering
        st.header("Clustering Metrics")
        self.clustering_metric_df = self._extract_clustering_metrics()
        st.write(self.clustering_metric_df)

        # Cluster Metrics
        st.header("Cluster Configuration")
        # Deselect metrics for clustering
        self.metrics_columns_to_include_in_clustering = []
    
        # Drop or add columns from K-means clustering
        # Default values hand tuned based on clustering results
        algorithms_to_remove = []
        default_algorithm_choices = list(set(self.all_algorithm_options) - set(algorithms_to_remove))
        
        algoprithm_metrics_selection = st.multiselect(
            label="Select algorithm metrics to include", 
            options=self.all_algorithm_options,
            default=default_algorithm_choices
        )
        self.metrics_columns_to_include_in_clustering+=algoprithm_metrics_selection

        algoprithm_metrics_selection = st.multiselect(
            label="Select basic metrics to include", 
            options=self.all_basic_metric_options,
            default=["rightballscount_max","leftballscount_max"]
        )
        self.metrics_columns_to_include_in_clustering+=algoprithm_metrics_selection

        # Set the number of clusters
        num_clusters = st.number_input("Chose the number of clusters:", step=1)
        self.clustering_metric_df, self.kmeans = self._cluster_metrics(self.clustering_metric_df, num_clusters, self.metrics_columns_to_include_in_clustering)
        st.write(self.clustering_metric_df[['dataset_id', 'cluster']])
        st.write(self.kmeans.get_params())

        # Plot Reduced Data by Cluster
        st.header("Reduced Data by Cluster")
        self._plot_reduced_data_by_cluster(self.clustering_metric_df, self.kmeans, self.metrics_columns_to_include_in_clustering)

        # Plot Metrics by Cluster
        st.header("Cluster Metric Individual Plots")
        self._plot_metrics_by_cluster(self.metrics_columns_to_include_in_clustering)

        # Examine Outlier
        self._examine_outlier()

    def _get_metrics_file(self):
        metrics_file = st.file_uploader("Upload metrics file", type=["json"])
        metrics_file = json.load(metrics_file)
        metrics_file = {
            "all_metrics": metrics_file["normalized_algorithm_metrics"],
            "all_basic_data_metrics": metrics_file["normalized_basic_metrics"]
        }
        # st.json(metrics_file)
        return metrics_file

    def _extract_clustering_metrics(self):
        st.subheader("Select Metrics for Clustering")

        algorithm_type_selections = list(self.metrics.keys())

        # Extract metric data
        first_metric = True
        metrics_df = pd.DataFrame()

        # Initialize lists of algorithms
        self.all_algorithm_options = []
        self.all_basic_metric_options = []

        algorithm_options = []
        for algorithm_type in algorithm_type_selections:
            algorithm_options = list(self.metrics[algorithm_type].keys())
            
            # Initialize dataframe with first metrics
            # TODO(jcm-art): Impelemnt more robust method for intializing
            if first_metric:
                metrics_df['dataset_id'] = self.metrics[algorithm_type][algorithm_options[0]]['dataset_id']
                first_metric = False

            for algorithm in algorithm_options:
                # Get metric options from algorithmn
                metric_options = self.metrics[algorithm_type][algorithm].keys()
                
                for metric in metric_options:
                    if metric != "dataset_id" and metric[-3:] != "min":
                        metrics_df[algorithm+"_"+metric] = self.metrics[algorithm_type][algorithm][metric]

                        if algorithm_type == "all_metrics":
                            self.all_algorithm_options.append(algorithm+"_"+metric)
                        else:
                            self.all_basic_metric_options.append(algorithm+"_"+metric)


        return metrics_df
    

    def _cluster_metrics(self, input_df, num_clusters, columns_to_cluser):

        cleaned_input_df = input_df[columns_to_cluser]

        # Perform k-means clustering
        k = num_clusters  # Specify the number of clusters
        kmeans = KMeans(n_clusters=k)
        kmeans.fit(cleaned_input_df)

        # Get cluster labels
        cluster_labels = kmeans.labels_

        # Add cluster labels to the DataFrame
        input_df['cluster'] = cluster_labels

        return input_df, kmeans
    
    def _plot_reduced_data_by_cluster(self, clustering_metric_df, kmeans, kmeans_columns):
        
        # Drop columns from K-means clustering
        pca_dataframe = clustering_metric_df[kmeans_columns]


        # Reduce dimensionality to 2D using PCA
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(pca_dataframe)

        # Create DataFrame for plotting
        df = pd.DataFrame({'PC1': X_pca[:, 0], 'PC2': X_pca[:, 1], 'Cluster': kmeans.labels_, 'label': clustering_metric_df.dataset_id})

        # Plot clusters using Plotly
        fig = px.scatter(df, x='PC1', y='PC2', color='Cluster', title='K-Means Clustering (2D PCA Projection)',
                        hover_name='label', 
                        labels={'PC1': 'Principal Component 1', 'PC2': 'Principal Component 2'}, 
                        color_continuous_scale='viridis')

        # Plot cluster centers
        cluster_centers = pca.transform(kmeans.cluster_centers_)
        fig.add_scatter(x=cluster_centers[:, 0], y=cluster_centers[:, 1], mode='markers', 
                        marker=dict(color='white', symbol='x', size=10), name='Cluster Centers')

        st.write(fig)


        return X_pca

    def _plot_metrics_by_cluster(self, plot_options):

        metric_columns = st.multiselect(
            label="Select what metrics to explore.",
            options=plot_options,
            default=plot_options[0]
        )
        
        for column in metric_columns:
            if column == "dataset_id" or column == "cluster":
                continue

            clustering_data = []

            tmp_scatter = go.Scatter(
                x=self.clustering_metric_df['dataset_id'], 
                y=self.clustering_metric_df[column],
                name=f"{column}",
                mode='markers',
                marker=dict(
                    size=8,
                    color=self.clustering_metric_df['cluster'],  # Color points based on values in column D
                    opacity=0.8
                )
            )

            clustering_data.append(tmp_scatter)

            clustering_layout = go.Layout(
                title=f'Metric Plot for {column}',
                barmode='overlay',
                xaxis=dict(
                    title='dataset_id'
                ),
                yaxis=dict(
                    title=f"Dataset {column} Column"
                ),
            )

            clustering_data_fig = go.Figure(data=clustering_data, layout = clustering_layout)
            
            # Plot time series
            st.write(clustering_data_fig)

    def _examine_outlier(self):

        selected_user = st.selectbox(
            "Select a dataset ID",
              options=self.clustering_metric_df['dataset_id']
        )       

        # Selecting the row with dataset_id=19
        single_row = self.clustering_metric_df[self.clustering_metric_df['dataset_id'] == selected_user].iloc[0]
        st.write(single_row)
        single_row = single_row.drop(index='dataset_id')
        single_row = single_row.drop(index='cluster')
        st.write(single_row)

        # Transpose the single row and rename index with original column names
        transposed_row = single_row.rename_axis('Metric Names').reset_index()
        transposed_row = transposed_row.rename(columns={transposed_row.columns[1]: 'metric_values'})

        # Sort the transposed row by values
        sorted_row = transposed_row.sort_values(by='Metric Names')

        # Plotting using Plotly Graph Objects
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=sorted_row['Metric Names'], y=sorted_row['metric_values'], mode='markers+lines'))
        fig.update_layout(title='Sorted Single Row Values with Original Column Names', xaxis_title='Columns', yaxis_title='Values')
        
        st.write(fig)