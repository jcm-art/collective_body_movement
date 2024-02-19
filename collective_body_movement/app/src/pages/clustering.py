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
        st.header("Clusters")
        # Set the number of clusters
        num_clusters = st.number_input("Chose the number of clusters:", value=3, step=1)
        # Drop columns from K-means clustering
        # Default values hand tuned based on clustering results
        columns_to_drop = st.multiselect(
            label="Select columns to drop",
            options=self.clustering_metric_df.columns,
            default=["dataset_id"]
        )
        self.clustering_metric_df, self.kmeans = self._cluster_metrics(self.clustering_metric_df, num_clusters, columns_to_drop)
        st.write(self.clustering_metric_df[['dataset_id', 'cluster']])
        st.write(self.kmeans.get_params())

        # Plot Reduced Data by Cluster
        st.header("Reduced Data by Cluster")
        self._plot_reduced_data_by_cluster(self.clustering_metric_df, self.kmeans)

        # Plot Metrics by Cluster
        st.header("Cluster Metric Individual Plots")
        self._plot_metrics_by_cluster()

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

        algorithm_type_options = list(self.metrics.keys())
        algorithm_type_selections = st.multiselect(
            label="Explore Basic Metrics or Algorithms?",
            options=algorithm_type_options,
        )

        # Extract metric data
        first_metric = True
        metrics_df = pd.DataFrame()

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


        return metrics_df
    

    def _cluster_metrics(self, input_df, num_clusters, columns_to_drop):

        cleaned_input_df = input_df.drop(columns=columns_to_drop)

        # Perform k-means clustering
        k = num_clusters  # Specify the number of clusters
        kmeans = KMeans(n_clusters=k)
        kmeans.fit(cleaned_input_df)

        # Get cluster labels
        cluster_labels = kmeans.labels_

        # Add cluster labels to the DataFrame
        input_df['cluster'] = cluster_labels

        return input_df, kmeans
    
    def _plot_reduced_data_by_cluster(self, clustering_metric_df, kmeans):
        
        # Drop columns from K-means clustering
        pca_dataframe = clustering_metric_df.drop(columns=["dataset_id", "cluster"])


        # Reduce dimensionality to 2D using PCA
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(pca_dataframe)

        # Create DataFrame for plotting
        df = pd.DataFrame({'PC1': X_pca[:, 0], 'PC2': X_pca[:, 1], 'Cluster': kmeans.labels_})

        # Plot clusters using Plotly
        fig = px.scatter(df, x='PC1', y='PC2', color='Cluster', title='K-Means Clustering (2D PCA Projection)', 
                        labels={'PC1': 'Principal Component 1', 'PC2': 'Principal Component 2'}, 
                        color_continuous_scale='viridis')

        # Plot cluster centers
        cluster_centers = pca.transform(kmeans.cluster_centers_)
        fig.add_scatter(x=cluster_centers[:, 0], y=cluster_centers[:, 1], mode='markers', 
                        marker=dict(color='white', symbol='x', size=10), name='Cluster Centers')

        st.write(fig)


        return X_pca

    def _plot_metrics_by_cluster(self):

        metric_columns = self.clustering_metric_df.columns
        
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

