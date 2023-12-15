# Collective Body Movement Application
# Director: Sarah Silverblatt-Buser (https://www.sarahsilverblatt.com/)
# Author: Justin Martin (jcm-art)

import numpy as np
import pandas as pd
from typing import Dict, List

from ..utils import CollectiveBodyLogger, CollectiveBodyBolt

class TimeAverageBolt(CollectiveBodyBolt):

    def __init__(
            self, 
            output_directory_path: str, 
            save_intermediate_output: bool, 
            window_size: int = 10) -> None:
        # Initialize template class
        super().__init__(output_directory_path, save_intermediate_output)

        # Store window size for bolt
        self.window_size = window_size
  
        # Initialize logger
        self.logger = CollectiveBodyLogger(__class__.__name__)

    def process(
        self, 
        input_dataframe_list: List[pd.DataFrame], 
        aggregate_metadata: Dict,
        input_metadata_list: List[Dict]
     ) -> (List[pd.DataFrame], List[Dict]):
        
        self.output_df_list = input_dataframe_list
        self.aggregate_metadata_output = aggregate_metadata
        self.output_metadata_list = input_metadata_list

        self.output_df_list, self.output_metadata_list = self._process_all_datasets(self.output_df_list, self.output_metadata_list)

        if self.save_intermediate_output:
            self.save_output()
            
        return self.output_df_list, self.aggregate_metadata_output, self.output_metadata_list

    def _process_all_datasets(self, df_list, metadata_list):
        """"Process functiont to take a metadata disctionary with file paths and
        preprocess and clean them."""
        output_df_list = df_list
        output_metadata_list = metadata_list

        assert len(self.output_df_list) == len(self.output_metadata_list), "Missing matching df and metadata pairs"
        for i in range(len(self.output_df_list)):
            output_df = self.output_df_list[i]

            # Prepare metadata for parsing and additions
            output_metadata = output_metadata_list[i]
            output_dataset_id = list(output_metadata.keys())[0]
            output_metadata = output_metadata[output_dataset_id]

            # Time average all data
            if output_metadata["cleaned_metadata"]["is_valid"]:
                self._log_output(f"Time averaging data for {output_dataset_id} with window size: {self.window_size}")
                output_df = self._smooth_and_downsample_location(output_df)
                output_metadata["filtering_metadata"] = {
                    "filter_type": "time_averaging",
                    "window_size": self.window_size,
                }
            else: 
                self._log_output(f"Invalid dataset, id: {output_dataset_id}")

                output_metadata["fundamental_kinematics_metadata"] = {
                    "error_flag": "invalid dataset, kinematics pipeline not run"
                }

            # Restore structure of output metdata
            output_metadata = {
                output_dataset_id: output_metadata
            }

            # Update the metadata list entries
            output_df_list[i] = output_df
            output_metadata_list[i] = output_metadata


        return output_df_list, output_metadata_list


    def _smooth_and_downsample_location(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Smooth and downsample accelerometer data using time averaging.

        Parameters:
        - data: pandas DataFrame with 'x', 'y', 'z', 'i', 'j', 'k', 'l' and 'timestamp' 
        columns for multiple sensors
        - window_size: Size of the window for time averaging.

        Returns:
        - Smoothed and downsampled DataFrame.
        """
        # Sort the data based on the timestamp
        data = data.sort_values(by='timestamp')

        # Columns to smooth
        columns_to_smooth = [
            "head_pos_x","head_pos_y","head_pos_z","left_pos_x","left_pos_y",
            "left_pos_z","right_pos_x","right_pos_y","right_pos_z","bigball_pos_x",
            "bigball_pos_y","bigball_pos_z","head_rot_i","head_rot_j","head_rot_k",
            "head_rot_l","left_rot_i","left_rot_j","left_rot_k","left_rot_l",
            "right_rot_i","right_rot_j","right_rot_k","right_rot_l",
        ]
        columns_to_down_sample = [
            "time","chapitre","leftballscount","rightballscount","dataset_id",
            "headset_number","session_number","timestamp","elapsed_time"
        ]

        # Apply time averaging for each column ('x', 'y', 'z', 'i', 'j', 'k')
        smoothed_data = data[columns_to_smooth].rolling(window=self.window_size).mean()

        # Downsample by selecting every nth row
        downsampled_data = smoothed_data.iloc[::self.window_size]
        downsampled_data=downsampled_data.reset_index()

        # Add timestamp column back to the downsampled data
        other_downsample_data = data[columns_to_down_sample].iloc[::self.window_size]   
        other_downsample_data=other_downsample_data.reset_index()

        # TODO - confirm more efficient way to concat
        downsampled_data=other_downsample_data.join(downsampled_data, how='left',rsuffix='r')
        downsampled_data.drop(columns=['indexr'], inplace=True)

        return downsampled_data

    def _log_output(self, output):
        print(f"{__class__.__name__}: {output}")