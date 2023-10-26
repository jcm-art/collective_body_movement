# Collective Body Movement Application
# Director: Sarah Silverblatt-Buser (https://www.sarahsilverblatt.com/)
# Author: Justin Martin (jcm-art)

import os
import pathlib
from typing import Dict, List

import pandas as pd

from ..utils import CollectiveBodyLogger, CollectiveBodyBolt

class DirectoryParserBolt(CollectiveBodyBolt):
    # TODO - reimplement as subclassof collective body bolt

    def __init__(self, output_directory_path: str, save_intermediate_output: bool) -> None:
        super().__init__(output_directory_path, save_intermediate_output)

        self.logger = CollectiveBodyLogger(class_name=__class__.__name__)
        self.logger.log("Initialized.")

    def process(
        self, 
        input_dataframe_list: List[pd.DataFrame], 
        aggregate_metadata: Dict,
        input_metadata_list: List[Dict]
     ) -> (List[pd.DataFrame], List[Dict]):
        """Process funtion to take input metadata containing a directory root path
        and discovered data files in that directory."""
        self.output_df_list = input_dataframe_list
        self.aggregate_metadata_output = aggregate_metadata
        self.output_metadata_list = input_metadata_list

        output_metadata =  self.aggregate_metadata_output

        discovered_paths = self._find_file_paths(
            output_metadata['input_metadata']['directory_root_path'])
    
        # Cap ingest files if file ingest limit provided
        quick_debug_mode = output_metadata['input_metadata']['quick_debug_mode']
        file_ingest_limit = output_metadata['input_metadata']['file_ingest_limit']
        if  quick_debug_mode and file_ingest_limit is not None:
            discovered_paths = discovered_paths[0:file_ingest_limit]
        
        # Store discovered filepaths
        output_metadata['input_metadata']['discovered_filepaths'] = discovered_paths

        self.aggregate_metadata_output = output_metadata

        if self.save_intermediate_output:
            self.save_output()
        
        return self.output_df_list, self.aggregate_metadata_output, self.output_metadata_list

    def _find_file_paths(self, directory_root_path: str) -> Dict:
        self.logger.log("Discovering file paths in root directory.")

        # Identify filepaths in root directory
        print(directory_root_path)
        input_path = pathlib.Path(directory_root_path)
        filepaths_in_directory = self._get_data_paths(input_path, ".csv")

        self.logger.log("Returning discovered file paths")
        return filepaths_in_directory


    def _get_data_paths(self, filepath, filetype):
        paths = []
        for root, dirs, files in os.walk(filepath):
            for file in files:
                if file.lower().endswith(filetype.lower()):
                    paths.append(str(pathlib.PurePath(root, file)))
        
        return paths



