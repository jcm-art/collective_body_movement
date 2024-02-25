# Collective Body Movement Application
# Director: Sarah Silverblatt-Buser (https://www.sarahsilverblatt.com/)
# Author: Justin Martin (jcm-art)

from abc import abstractmethod
import json
import pathlib
import time
from typing import Dict, List

import pandas as pd

class CollectiveBodyBolt:

    def __init__(self, output_directory_path: str, save_intermediate_output: bool=False) -> None:
        # initialize dataframe and metadata for bolt
        self.output_df_list: List[pd.DataFrame] = []
        self.aggregate_metadata_output = {}
        self.output_metadata_list: List[Dict] = []

        # Initialize output for bolt
        self.save_intermediate_output = save_intermediate_output
        if save_intermediate_output:
            output_directory= pathlib.Path(output_directory_path)
            self.output_path = output_directory/f"{__class__.__name__}_output/"
            self.output_path.mkdir(parents=True, exist_ok=True)      

    @abstractmethod
    def process(
        self, 
        input_dataframe_list: List[pd.DataFrame], 
        aggregate_metadata: Dict,
        input_metadata_list: List[Dict]
     ) -> (List[pd.DataFrame], List[Dict]):
        """Process method that transforms a dataframe must be implemented for every"""

    def save_output(self):
        # Save aggregate metadata
        json_output = self.output_path/f"{__class__.__name__}_aggregate_metadata.json"
        with open(json_output,"w") as outfile:
            # TODO - validate that posix path and datetime aren't broken with forced default str output
            json_object = json.dumps(self.aggregate_metadata_output, indent = 6, sort_keys=True, default=str) 
            outfile.write(json_object)

        # Save dataset metadata
        for single_dataset_metadata, dataset_to_save  in zip(self.output_metadata_list, self.output_df_list):
            # Extract Dataset IT
            dataset_id = single_dataset_metadata[list(single_dataset_metadata.keys())[0]]['cleaned_metadata']['dataset_id']

            json_output = self.output_path/f"{__class__.__name__}_{dataset_id}.json"
            with open(json_output,"w") as outfile:
                # TODO - validate that posix path and datetime aren't broken with forced default str output
                json_object = json.dumps(single_dataset_metadata, indent = 6, sort_keys=True, default=str) 
                outfile.write(json_object)

            dataframe_output = self.output_path/f"{__class__.__name__}_{dataset_id}.csv"
            dataset_to_save.to_csv(dataframe_output, index=True)

    def print_intermediate_metadata(self):
        # TODO - consider using logger
        print(f"{__class__.__name__}: Intermediate Bolt Metadata")
        for counter in range(len(self.output_metadata_list)):
            single_dataset_metadata = self.output_metadata_list[counter]
            dataset_id = single_dataset_metadata.keys()[0]
            print(f"Metadata for Dataset ID: {dataset_id}/n")
            print(self.output_metadata_list[counter])

    @classmethod
    def clear_bolt(self):
        self.output_df_list: List[pd.DataFrame] = []
        self.aggregate_metadata_output = {}
        self.output_metadata_list: List[Dict] = []


class CollectiveBodyLog:
    # TODO - rewrite as struct
    def __init__(self, log_time: float, class_name: str, log_text: str) -> None:
        self._log_dict = {
            "time": log_time,
            "class_name": class_name,
            "log_text": log_text
        }

    def get_dict(self):
        return self._log_dict

    def __str__(self) -> str:
        return f"{self._log_dict['time']}|{self._log_dict['class_name']}: {self._log_dict['log_text']}"

class CollectiveBodyLogger:

    def __init__(self, class_name: str, print_logs: bool=True) -> None:
        self.class_name = class_name
        self.print_logs = print_logs
        self.log_list = []

    def log(self, log_text):
        new_log = CollectiveBodyLog(time.time(), self.class_name, log_text)
        self.log_list.append(new_log)
        if self.print_logs:
            print(new_log)