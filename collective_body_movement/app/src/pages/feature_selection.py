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


class FeatureSelectionPage(StreamlitPage):

    def __init__(self, state):
        self.state = state

    def write(self):
        st.title("Feature Selection")

        # Get and display metric data 
        st.header("Load Metrics")
        self.metrics = self._get_metrics_file()

        # Extract metrics 
        st.header("Feature Correlation")
        # Set threshold for correlation
        self.correlation_threshold = 0.7  # You can adjust this threshold as needed
        self.clustering_metric_df = self._extract_clustering_metrics()

        # Get covariance matrix
        self.correlation_matrix, self.highly_correlated_features = self._calculate_correlation(self.clustering_metric_df)

        # Get ranked PCA
        self.feature_contributions, self.ranked_features = self._ranked_pca(self.clustering_metric_df, self.columns_to_include)

        # Print feature correlation rankings and statistics
        self._print_feature_selection_help()

        # Write details
        self._write_details()

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
    
    def _manual_cleaning(self, input_df):
        # Drop unnecessary columns from dataset
        columns_to_exclude = [
            'dataset_id',
            "chapitre_max",
            "chapitre_mean",
            "chapitre_std",
            "chapitre_sum",
            "dataset_id_max",
            "dataset_id_mean",
            "dataset_id_std",
            "dataset_id_sum",
            "elapsed_time_max",
            "elapsed_time_mean",
            "elapsed_time_std",
            "elapsed_time_sum",
            "headset_number_mean",
            "headset_number_max",
            "headset_number_sum",
        ]
        cleaned_input_df = input_df.drop(columns=columns_to_exclude)
        return cleaned_input_df

    def _calculate_correlation(self, input_df):

        # Clean input data
        cleaned_input_df = self._manual_cleaning(input_df)
        
        # Prefill by chapter 
        chapter_filter = st.selectbox(
            "Select Chapter", options=["1","2","3","All","No Filter"],
            index=4
        )

        prefilled_default = None
        if chapter_filter is not "No Filter":
            prefilled_default = list(cleaned_input_df.filter(like=chapter_filter).columns)

        self.columns_to_include = st.multiselect(
            "Select columns for covariance matrix", 
            options=cleaned_input_df.columns,
            default=prefilled_default
        )     

        # Perform k-means clustering
        filtered_df = cleaned_input_df[self.columns_to_include]
        correlation_matrix = filtered_df.corr()

        # Find highly correlated features
        highly_correlated_features = list()
        self.highly_correlated_features_dict = {}
        for i in range(len(correlation_matrix.columns)):
            for j in range(i):
                if abs(correlation_matrix.iloc[i, j]) > self.correlation_threshold:
                    colname = correlation_matrix.columns[i]
                    rowname = correlation_matrix.index[j]
                    score = correlation_matrix.iloc[i, j]
                    highly_correlated_features.append((colname, rowname))
                    self.highly_correlated_features_dict[score] = (colname, rowname)


        return correlation_matrix, highly_correlated_features

    def _ranked_pca(self, input_df, columns_to_include):

        # Clean input data
        cleaned_input_df = input_df[columns_to_include]


        # Perform PCA
        pca = PCA()
        pca.fit(cleaned_input_df)

        # Get the principal components
        principal_components = pca.components_

        # Create DataFrame to store feature contributions to each PCA dimension
        feature_contributions = pd.DataFrame(principal_components, columns=cleaned_input_df.columns)

        # Calculate absolute values of feature contributions
        feature_contributions = np.abs(feature_contributions)

        # Rank features for each PCA dimension based on contribution
        ranked_features = feature_contributions.apply(lambda x: x.sort_values(ascending=False).index, axis=1)


        # Plot PCA factors
        self.fig_pca_factor = px.bar(x=range(1, pca.n_components_ + 1), y=pca.explained_variance_ratio_, 
                            labels={'x': 'Principal Components', 'y': 'Explained Variance Ratio'},
                            title='PCA Factor Plot')
        self.fig_pca_factor.update_traces(marker=dict(color='skyblue'))
        self.fig_pca_factor.update_layout(showlegend=False)

        # Plot PCA scores
        pca_scores = pca.transform(cleaned_input_df)
        self.fig_pca_scores = px.scatter(x=pca_scores[:, 0], y=pca_scores[:, 1], 
                                labels={'x': 'Principal Component 1', 'y': 'Principal Component 2'},
                                title='PCA Scores Plot')
        self.fig_pca_scores.update_traces(marker=dict(color='green', opacity=0.5))

        return feature_contributions, ranked_features
    
    def _print_feature_selection_help(self):

        st.header("Feature Selection Help")
        st.write("Highly correlated features based on a threshold of", self.correlation_threshold, ":")
        
        st.write(self.correlation_matrix)

        sorted_scores = list(self.highly_correlated_features_dict.keys())
        sorted_scores.sort(reverse=True)

        for score in sorted_scores:
            correlated_pairs = self.highly_correlated_features_dict[score]
            subheader_string = "Correlated pair (score "+str(self.correlation_matrix.loc[correlated_pairs[1],correlated_pairs[0]])+"):"
            st.subheader(subheader_string)
            for i, feature in enumerate(correlated_pairs):
                st.write("Feature ",i+1,". ", feature)

                # Extract feature information and scoring
                for j in range(0,2):
                    pca_feature_index = self.ranked_features.values[j].tolist()
                    pca_rank = pca_feature_index.index(feature)
                    pca_score = self.feature_contributions.loc[j, feature]
                    st.write("\tPCA Factor ",str(j+1),"| Rank: ", pca_rank," PCA",j+1," Score: ", pca_score)

        
    def _write_details(self):

        # Calculate factor covariance
        st.write(self.correlation_matrix)

        # PCA details
        st.write("Feature contributions to each PCA dimension:")
        st.write(self.feature_contributions)
        st.write(self.fig_pca_factor)
        st.write(self.fig_pca_scores)

        # Print ranked features for each PCA dimension
        for i, dimension_features in enumerate(self.ranked_features.values):
            st.write(f"PCA Dimension {i+1} Top Contributing Features:")
            for j, feature in enumerate(dimension_features):
                st.write(f"{j+1}. {feature}: {self.feature_contributions.loc[i, feature]}")
            st.write()