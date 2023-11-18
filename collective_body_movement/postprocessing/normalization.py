# Collective Body Movement Application
# Director: Sarah Silverblatt-Buser (https://www.sarahsilverblatt.com/)
# Author: Justin Martin (jcm-art)

from typing import Dict, List
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

        self.aggregate_metadata_output["final_aggregation_metadata"] = {}

        self.aggregate_metadata_output, self.aggregate_metadata_output, self.output_metadata_list = self._purge_invalid_datasets(
            self.output_df_list, self.aggregate_metadata_output, self.output_metadata_list)


        self.aggregate_metadata_output, self.output_metadata_list = self._merge_metadata(
            self.aggregate_metadata_output, self.output_metadata_list)
        
        self.aggregate_metadata_output, self.output_metadata_list = self._purge_metadata(
            self.aggregate_metadata_output, self.output_metadata_list)

        self.output_df_list, self.aggregate_metadata_output = self._purge_intermediate_columns(
            self.output_df_list, self.aggregate_metadata_output)

        if self.save_intermediate_output:
            self.save_output()
            
        return self.output_df_list, self.aggregate_metadata_output, self.output_metadata_list
    

    def _normalize_datasets(
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


    def _normalize_mettrics(
            self, 
        aggregate_metadata: Dict,
        input_metadata_list: List[Dict],
     ) -> (List[pd.DataFrame], List[Dict]):
        
        ouput_aggregate_metadata = aggregate_metadata
        output_metadata_list = input_metadata_list

        ouput_aggregate_metadata["all_metrics"] = {}

        for i in range(len(output_metadata_list)):
            metadata = output_metadata_list[i]
            dataset_id = list(metadata.keys())[0]

            metrics_metadata = metadata[dataset_id]["metrics"]

            for algorithm_key in metrics_metadata.keys():
                # Create dictionary for algorithm if not available
                if algorithm_key not in ouput_aggregate_metadata["all_metrics"]:
                    ouput_aggregate_metadata["all_metrics"][algorithm_key]={}

                for metric_type in metrics_metadata[algorithm_key].keys():
                    # Check if metric type already in aggregate data
                    if metric_type not in ouput_aggregate_metadata["all_metrics"][algorithm_key]:
                        ouput_aggregate_metadata["all_metrics"][algorithm_key][metric_type] = []
                    
                    # Append metric to aggregate data
                    ouput_aggregate_metadata["all_metrics"][algorithm_key][metric_type]+= \
                        metrics_metadata[algorithm_key][metric_type]

                    # Todo - if appending more than 




        return ouput_aggregate_metadata, output_metadata_list