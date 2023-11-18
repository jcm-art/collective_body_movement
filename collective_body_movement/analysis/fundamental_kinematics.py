# Collective Body Movement Application
# Director: Sarah Silverblatt-Buser (https://www.sarahsilverblatt.com/)
# Author: Justin Martin (jcm-art)

from typing import Dict, List

import numpy as np
import pandas as pd

from ..utils import CollectiveBodyBolt

class FundamentalKinematicsBolt(CollectiveBodyBolt):

    def __init__(self, output_directory_path: str, use_smoothing: bool=False, save_intermediate_output: bool=False) -> None:
        super().__init__(output_directory_path, save_intermediate_output)

        self.use_smoothing = use_smoothing
        self.sensor_locations = ['head','left','right']
        self.motion_types = ['pos','rot']
        self.pos_axes = ['x','y','z']
        self.rot_axes = ['i','j','k','l']

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

    def _process_all_datasets(self, output_df_list, output_metadata_list):

        assert len(output_df_list) == len(output_metadata_list), "Missing matching df and metadata pairs"
        for i in range(len(output_df_list)):
            output_df = output_df_list[i]

            # Prepare metadata for parsing and additions
            output_metadata = output_metadata_list[i]
            output_dataset_id = list(output_metadata.keys())[0]
            output_metadata = output_metadata[output_dataset_id]
            output_metadata["fundamental_kinematics_metadata"] = {}

            if output_metadata["cleaned_metadata"]["is_valid"]:
                output_df, output_metadata = self._basic_kinematics(output_df, output_metadata)

            else: 
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

    def _basic_kinematics(self, output_df: pd.DataFrame, output_metadata: Dict):
        # TODO - build list of algorithms to use for final metrics per dataset

        # Set timestep for calculations
        output_metadata = self._add_average_frame_timestep(output_metadata)

        # Calculate basic kinematics properties for metrics calculations
        output_df, output_metadata = self._calculate_velocities(output_df, output_metadata)
        output_df, output_metadata = self._calculate_accelerations(output_df, output_metadata)
        output_df, output_metadata = self._calculate_jerk(output_df, output_metadata)
        output_df, output_metadata = self._calculate_kinematic_magnitudes(output_df, output_metadata)
        output_df, output_metadata = self._calculate_moment_arms(output_df, output_metadata)
        output_df, output_metadata = self._calculate_xzplanar_moment_arm_mag(output_df, output_metadata)

        return output_df, output_metadata

    def _add_average_frame_timestep(self, output_metadata) -> Dict:
        elapsed_time = output_metadata["cleaned_metadata"]["elapsed_time"]
        total_frames = output_metadata["cleaned_metadata"]["num_frames"]
        timestep = elapsed_time / 1000 / total_frames
        output_metadata["fundamental_kinematics_metadata"]["avg_timestep"] = timestep
        return output_metadata

    def _calculate_velocities(self, output_df: pd.DataFrame, output_metadata: Dict):
        return self._kinematics_derivative(output_df, output_metadata, "", "vel_")
    
    def _calculate_accelerations(self, output_df: pd.DataFrame, output_metadata: Dict):
        return self._kinematics_derivative(output_df, output_metadata, "vel_", "accel_")
    
    def _calculate_jerk(self, output_df: pd.DataFrame, output_metadata: Dict):
        return self._kinematics_derivative(output_df, output_metadata, "accel_", "jerk_")
    
    def _kinematics_derivative(
            self, 
            output_df: pd.DataFrame,
            output_metadata: Dict,
            base_str: str, 
            new_str: str):
        timestep = output_metadata["fundamental_kinematics_metadata"]["avg_timestep"]

        # Calculate linear and rotational velocities
        for sensor_pos in self.sensor_locations:
            for motion_type in self.motion_types:

                # Separete rotation and position
                if motion_type == "rot":
                    motion_axes = self.rot_axes
                elif motion_type == "pos":
                    motion_axes = self.pos_axes

                for motion_axis in motion_axes:
                    base_col_name = "_".join((sensor_pos, base_str+motion_type, motion_axis))
                    new_col_name = "_".join((sensor_pos, new_str+motion_type, motion_axis))
                    output_df = self._derivative(output_df, base_col_name, new_col_name, timestep)

                    output_df[new_col_name].fillna(0, inplace=True)
                    # TODO - add metadata to velocities using custom class to report stats

                    # Smooth derivatives if bolt configured for smoothing
                    if self.use_smoothing:
                        output_df = self._clip_derivatives(output_df, new_col_name)


        return output_df, output_metadata

    def _calculate_kinematic_magnitudes(self, output_df: pd.DataFrame, output_metadata: Dict):
        kinematics_magnitudes = ["vel", "accel", "jerk"]

        for sensor_pos in self.sensor_locations:
            for magval in kinematics_magnitudes:
                for motion_type in self.motion_types:
                    # Separate rotation and position
                    if motion_type == "rot":
                        motion_axes = self.rot_axes
                    elif motion_type == "pos":
                        motion_axes = self.pos_axes

                    magnitude_field = "_".join((sensor_pos, magval, motion_type, "magnitude"))
                    fields = []
                    for axis in motion_axes:
                        fields.append("_".join((sensor_pos, magval,motion_type,axis)))

                    output_df = self._magnitude_lambda(output_df, magnitude_field, fields)
        return output_df, output_metadata
    
    def _magnitude_lambda(self, output_df: pd.DataFrame, magnitude_field: str, fields: List[str]):
        if len(fields) == 3:
            output_df = output_df.assign(
                magnitude_field_tmp=lambda x: (
                    (x[fields[0]]**2 + x[fields[1]]**2 + x[fields[2]]**2)**0.5
                )
            )
        elif len(fields) == 4:
            output_df = output_df.assign(
                magnitude_field_tmp=lambda x: (
                    (x[fields[0]]**2 + x[fields[1]]**2 + x[fields[2]]**2 + x[fields[3]]**2)**0.5
                )
            ) 

        # Rename temporary columns prior to returning
        output_df.rename(columns={'magnitude_field_tmp':magnitude_field}, inplace=True)
        return output_df

    def _calculate_moment_arms(self, output_df: pd.DataFrame, output_metadata: Dict):
        # TODO - implement moment arms
        return output_df, output_metadata
    
    def _calculate_xzplanar_moment_arm_mag(self, output_df: pd.DataFrame, output_metadata: Dict):
        output_df = output_df.assign(
                left_xzplanar_moment_arm_len=lambda x: (
                    ((x["left_pos_x"]-x["head_pos_x"])**2 + (x["left_pos_z"]-x["head_pos_z"])**2)**0.5
                )
            )
        
        output_df = output_df.assign(
                right_xzplanar_moment_arm_len=lambda x: (
                    ((x["right_pos_x"]-x["head_pos_x"])**2 + (x["right_pos_z"]-x["head_pos_z"])**2)**0.5
                )
            )
        return output_df, output_metadata


    def _derivative(
            self, 
            df:pd.DataFrame, 
            old_column_name: str, 
            new_column_name: str, 
            timestep: float):
        
        df[new_column_name] = df[old_column_name].diff() / timestep

        return df

    def _clip_derivatives(
            self,
            output_df: pd.DataFrame, 
            new_col_name:str):
        
        # Get data and max/min
        # TODO (jcm-art): replace with more efficient implementation
        data = output_df[new_col_name].to_numpy()
        data.sort()
        percentile_to_clip = 0.9
        upper_bound_index = int(len(data)*percentile_to_clip)
        upper_bound_val = data[upper_bound_index]

        # Clip upper bound
        output_df[new_col_name] = output_df[new_col_name].apply(
            lambda x: upper_bound_val if x > upper_bound_val else x)
        
        return output_df

        
