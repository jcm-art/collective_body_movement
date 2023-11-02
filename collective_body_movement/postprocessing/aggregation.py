# Collective Body Movement Application
# Director: Sarah Silverblatt-Buser (https://www.sarahsilverblatt.com/)
# Author: Justin Martin (jcm-art)

import json
from typing import Dict, List


import numpy as np
import pandas as pd
from ..utils import CollectiveBodyBolt
from collective_body_movement.analysis.metrics import MetricCalculator

class AggregatorBolt(CollectiveBodyBolt):

    def __init__(self, output_directory_path: str, save_intermediate_output: bool=False) -> None:
        super().__init__(output_directory_path, save_intermediate_output)
        self.metrics_categories = ["metrics", "basic_data_metrics"]

    def process(
        self, 
        input_dataframe_list: List[pd.DataFrame], 
        aggregate_metadata: Dict,
        input_metadata_list: List[Dict]
     ) -> (List[pd.DataFrame], List[Dict]):
        
        self.output_df_list = input_dataframe_list
        self.aggregate_metadata_output = aggregate_metadata
        self.output_metadata_list = input_metadata_list

        self.aggregate_metadata_output["final_aggregation_metadata"] = {}

        self.aggregate_metadata_output, self.aggregate_metadata_output, self.output_metadata_list = self._purge_invalid_datasets(
            self.output_df_list, self.aggregate_metadata_output, self.output_metadata_list)


        self.aggregate_metadata_output, self.output_metadata_list = self._merge_metadata(
            self.aggregate_metadata_output, self.output_metadata_list)
        
        # Get summary metrics for dervied metrics and for basic data
        self.aggregate_metadata_output = self._metric_metadata_summaries(self.aggregate_metadata_output)
        
        # self.aggregate_metadata_output, self.output_metadata_list = self._purge_metadata(
        #    self.aggregate_metadata_output, self.output_metadata_list)

        self.output_df_list, self.aggregate_metadata_output = self._purge_intermediate_columns(
            self.output_df_list, self.aggregate_metadata_output)

        if self.save_intermediate_output:
            self.save_output()
            
        return self.output_df_list, self.aggregate_metadata_output, self.output_metadata_list

    def _purge_invalid_datasets(
        self, 
        input_dataframe_list: List[pd.DataFrame], 
        aggregate_metadata: Dict,
        input_metadata_list: List[Dict]
     ) -> (List[pd.DataFrame], List[Dict]):
        
        indexes_to_purge = []
        dataset_ids_to_purge = []

        for i in range(len(input_metadata_list)):
            metadata = input_metadata_list[i]
            dataset_id = list(metadata.keys())[0]

            if metadata[dataset_id]["cleaned_metadata"]["is_valid"]==False:
                dataset_ids_to_purge.append(dataset_id)
                indexes_to_purge.append(i)

        indexes_to_purge.sort(reverse=True)
        # Delete invalid datasets
        for index in indexes_to_purge:
            del input_dataframe_list[index]
            del input_metadata_list[index]

        aggregate_metadata["final_aggregation_metadata"]["purged_datasets"] = dataset_ids_to_purge

        return input_dataframe_list, aggregate_metadata, input_metadata_list

    def _merge_metadata(
            self, 
        aggregate_metadata: Dict,
        input_metadata_list: List[Dict],
     ) -> (List[pd.DataFrame], List[Dict]):
        
        output_aggregate_metadata = aggregate_metadata
        output_metadata_list = input_metadata_list

        output_aggregate_metadata["all_metrics"] = {}
        output_aggregate_metadata["all_basic_data_metrics"] = {}

        # Merge metadata for all calculated metrics
        for i in range(len(output_metadata_list)):
            metadata = output_metadata_list[i]
            dataset_id = list(metadata.keys())[0]

            # TODO fix hard coding
            for metric_category in self.metrics_categories:
                metrics_metadata = metadata[dataset_id][metric_category]

                #print(json.dumps(metrics_metadata, indent=4))

                for algorithm_key in metrics_metadata.keys():
                    # Create dictionary for algorithm if not available
                    if algorithm_key not in output_aggregate_metadata[f"all_{metric_category}"]:
                        output_aggregate_metadata[f"all_{metric_category}"][algorithm_key]={}

                    for metric_type in metrics_metadata[algorithm_key].keys():
                        # Check if metric type already in aggregate data
                        if metric_type not in output_aggregate_metadata[f"all_{metric_category}"][algorithm_key]:
                            output_aggregate_metadata[f"all_{metric_category}"][algorithm_key][metric_type] = []
                        
                        # Append metric to aggregate data
                        metric_data = metrics_metadata[algorithm_key][metric_type]
                        output_aggregate_metadata[f"all_{metric_category}"][algorithm_key][metric_type]+= metric_data
                        
                        # print(f"Check: sum of data for alg: {algorithm_key}, met: {metric_type} is {np.sum(metric_data)}")


                        # Todo - if appending more than 

        return output_aggregate_metadata, output_metadata_list

    # TODO - move to separaete bolt to enable multiple aggregators
    def _metric_metadata_summaries(self, aggregate_metadata: Dict) -> Dict:
        output_aggregate_metadata = aggregate_metadata

        for metric_type in self.metrics_categories:
            output_aggregate_metadata[f"{metric_type}_summaries"] = {}

            # Get all algorithms in metrics
            algorithm_list = list(output_aggregate_metadata[f"all_{metric_type}"].keys())

            #print("Aggregate Metadata is \n\n")
            #print(json.dumps(output_aggregate_metadata, indent=4))


            # Get summary statistics for algoritms
            for algorithm in algorithm_list:
                output_aggregate_metadata[f"{metric_type}_summaries"][algorithm] = {}
                metric_options = list(output_aggregate_metadata[f"all_{metric_type}"][algorithm].keys())

                for metric in metric_options[1:]:
                    metric_data = output_aggregate_metadata[f"all_{metric_type}"][algorithm][metric]

                    #print(f"Check: sum of data for alg: {algorithm}, met: {metric} is {np.sum(metric_data)}")

                    total_dist_metric = MetricCalculator()
                    meta_metric_dict = total_dist_metric.calculate_meta_metrics(metric_data)
                    output_aggregate_metadata[f"{metric_type}_summaries"][algorithm][metric] = meta_metric_dict


        return output_aggregate_metadata
        
    def _purge_metadata(
            self, 
        aggregate_metadata: Dict,
        input_metadata_list: List[Dict],
     ) -> (List[pd.DataFrame], List[Dict]):
        # TODO - purge metadata list

        output_aggregate_metadata = aggregate_metadata
        output_metadata_list = input_metadata_list
        
        return output_aggregate_metadata, output_metadata_list

    def _purge_intermediate_columns(
            self, 
            df_list: List[pd.DataFrame], 
            aggregate_metadata: Dict
    ) -> (List[pd.DataFrame], Dict):
     
        output_df_list =df_list
        output_aggregate_metadata = aggregate_metadata

        # TODO - move to metadata and build as enabled
        columns_to_keep = ['time','chapitre','dataset_id','head_pos_x','head_pos_y',
                           'head_pos_z','left_pos_x','left_pos_y','left_pos_z','right_pos_x',
                           'right_pos_y','right_pos_z','head_rot_i','head_rot_j','head_rot_k',
                           'head_rot_l','left_rot_i','left_rot_j','left_rot_k','left_rot_l',
                           'right_rot_i','right_rot_j','right_rot_k','right_rot_l','timestamp',
                           'elapsed_time']
        dropped_columns = output_df_list[0].columns.difference(columns_to_keep)


        for i in range(len(output_df_list)):

            output_df_list[i].drop(dropped_columns, axis=1, inplace=True)

        return output_df_list, output_aggregate_metadata