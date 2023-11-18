# Collective Body Movement Application
# Director: Sarah Silverblatt-Buser (https://www.sarahsilverblatt.com/)
# Author: Justin Martin (jcm-art)

from typing import Dict, List
import numpy as np
import pandas as pd
from ..utils import CollectiveBodyBolt

class NormalizerBolt(CollectiveBodyBolt):

    def __init__(self, output_directory_path: str, save_intermediate_output: bool=False) -> None:
        super().__init__(output_directory_path, save_intermediate_output)

    def process(
        self, 
        input_dataframe_list: List[pd.DataFrame], 
        aggregate_metadata: Dict,
        input_metadata_list: List[Dict]
     ) -> (List[pd.DataFrame], List[Dict]):
        
        self.output_df_list = input_dataframe_list
        self.aggregate_metadata_output = aggregate_metadata
        self.output_metadata_list = input_metadata_list

        self.aggregate_metadata_output["normalization_output"] = {}


        self.aggregate_metadata_output, self.output_metadata_list = self._normalize_metrics(
            self.aggregate_metadata_output, self.output_metadata_list)
        
        self.output_df_list, self.aggregate_metadata_output, self.output_metadata_list = self._normalize_datasets(
            self.output_df_list, self.aggregate_metadata_output, self.output_metadata_list)
        

        if self.save_intermediate_output:
            self.save_output()
            
        return self.output_df_list, self.aggregate_metadata_output, self.output_metadata_list
    

    def _normalize_datasets(
        self, 
        input_dataframe_list: List[pd.DataFrame], 
        aggregate_metadata: Dict,
        input_metadata_list: List[Dict]
     ) -> (List[pd.DataFrame], List[Dict]):
        
        ouput_aggregate_metadata = aggregate_metadata
        output_metadata_list = input_metadata_list
        prior_basic_metrics = ouput_aggregate_metadata["all_basic_data_metrics"]

        min_max_dict = {
            'x':{},
            'y':{},
            'z':{},
        }

        for dim in min_max_dict.keys():

            # Get max and min values for norm
            combined_maxes = [] 
            combined_mins = [] 

            for sensor_location in ['head', 'left','right']:
                    combined_maxes = combined_maxes+prior_basic_metrics[f"{sensor_location}_pos_{dim}"]["max"]
                    combined_mins = combined_mins+prior_basic_metrics[f"{sensor_location}_pos_{dim}"]["min"]

            min_max_dict[dim]['max'] = np.max(combined_maxes)
            min_max_dict[dim]['min'] = np.min(combined_mins)
            print(f"min {min_max_dict[dim]['min']} max {min_max_dict[dim]['max']} and size of combined = {len(combined_maxes)}")
            min_max_dict[dim]['denom_value'] = min_max_dict[dim]['max'] - min_max_dict[dim]['min'] \
                if min_max_dict[dim]['max']-min_max_dict[dim]['min'] > 1e-4 else 1

        # Normalize position data
        for i in range(len(input_dataframe_list)):
            df = input_dataframe_list[i]
            for dim in ['x','y','z']:

                # Update sensors w/ normalized dimension
                for sensor_location in ['head', 'left','right']:
                    df[f"{sensor_location}_pos_{dim}"] = \
                        (df[f"{sensor_location}_pos_{dim}"] - \
                         min_max_dict[dim]['min'])/(min_max_dict[dim]['denom_value'])

            input_dataframe_list[i] = df


        return input_dataframe_list, aggregate_metadata, input_metadata_list


    def _normalize_metrics(
            self, 
        aggregate_metadata: Dict,
        input_metadata_list: List[Dict],
     ) -> (List[pd.DataFrame], List[Dict]):
        
        ouput_aggregate_metadata = aggregate_metadata
        output_metadata_list = input_metadata_list

        # Get un-normalized metrics
        prior_basic_metrics = ouput_aggregate_metadata["all_basic_data_metrics"]
        prior_algorithm_metrics = ouput_aggregate_metadata["all_metrics"]

        ouput_aggregate_metadata["normalized_basic_metrics"] = {}
        ouput_aggregate_metadata["normalized_algorithm_metrics"] = {}

        # Normalize basic metrics
        for algorithm_type in prior_basic_metrics.keys():

            norm_metric_dict = {}

            for metric_type in prior_basic_metrics[algorithm_type].keys():

                metric_arr = np.array(prior_basic_metrics[algorithm_type][metric_type])

                # Normalize each metric list                               
                if metric_type !="dataset_id": # Skip normalizing dataset ids 
                    # Get values for normalization
                    min_val = np.min(metric_arr)
                    max_val = np.max(metric_arr)
                    norm_denom = max_val - min_val if max_val - min_val > 1e-4 else 1

                    # Normalize and store new metric
                    metric_arr = (metric_arr - min_val)/norm_denom

                norm_metric_dict[metric_type] = metric_arr.tolist()

            ouput_aggregate_metadata["normalized_basic_metrics"][algorithm_type] = norm_metric_dict

        # Normalize algorithm metrics
        for algorithm_type in prior_algorithm_metrics.keys():

            norm_metric_dict = {}

            for metric_type in prior_algorithm_metrics[algorithm_type].keys():

                metric_list = prior_algorithm_metrics[algorithm_type][metric_type]
                metric_arr = np.array(metric_list)
                
                # Normalize each metric list                               
                if metric_type !="dataset_id": # Skip normalizing dataset ids 
                    # Get values for normalization
                    min_val = np.min(metric_arr)
                    max_val = np.max(metric_arr)
                    norm_denom = max_val - min_val if max_val - min_val > 1e-4 else 1

                    # Normalize and store new metric
                    metric_arr = (metric_arr - min_val)/norm_denom

                #print(f"keys: {algorithm_type}, {metric_type}, \n\n {metric_arr}")
                norm_metric_dict[metric_type] = metric_arr.tolist()
                #print(f"exception due to arr issue: {ouput_aggregate_metadata['normalized_algorithm_metrics']}")

            ouput_aggregate_metadata["normalized_algorithm_metrics"][algorithm_type] = norm_metric_dict

        return ouput_aggregate_metadata, output_metadata_list