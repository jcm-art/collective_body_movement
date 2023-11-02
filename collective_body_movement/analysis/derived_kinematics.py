# Collective Body Movement Application
# Director: Sarah Silverblatt-Buser (https://www.sarahsilverblatt.com/)
# Author: Justin Martin (jcm-art)

from typing import Dict, List
import pandas as pd

from ..utils import CollectiveBodyBolt

class DerivedKinematicsBolt(CollectiveBodyBolt):

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

        self.output_df_list, self.output_metadata_list = self._process_all_datasets(self.output_df_list, self.output_metadata_list)

        if self.save_intermediate_output:
            self.save_output()
            
        return self.output_df_list, self.aggregate_metadata_output, self.output_metadata_list

    def _process_all_datasets(self, output_df_list, output_metadata_list):

        assert len(output_df_list) == len(output_metadata_list), "Missing matching df and metadata pairs"
        for i in range(len(output_df_list)):
            output_df = output_df_list[i]

            # Prepare metadata for parsing and addifions
            output_metadata = output_metadata_list[i]
            output_dataset_id = list(output_metadata.keys())[0]
            output_metadata = output_metadata[output_dataset_id]
            output_metadata["derived_kinematics_metadata"] = {}

            if output_metadata["cleaned_metadata"]["is_valid"]:
                output_df, output_metadata = self._derived_kinematics(output_df, output_metadata)

            else: 
                output_metadata["derived_kinematics_metadata"] = {
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

    def _derived_kinematics(self, output_df: pd.DataFrame, output_metadata: Dict):

        output_df, output_metadata = self._cumulative_distance(output_df, output_metadata)
        output_df, output_metadata = self._cumulative_rotational_distance(output_df, output_metadata)
        
        return output_df, output_metadata
    

    def _cumulative_distance(self, output_df: pd.DataFrame, output_metadata: Dict):
        timestep = output_metadata["fundamental_kinematics_metadata"]["avg_timestep"]
    
        # Caculate displacement for every timestep
        output_df = output_df.assign(
                cartesian_displacement=lambda x: (
                    ((x["head_vel_pos_x"]*timestep)**2 + (x["head_vel_pos_y"]*timestep)**2 + (x["head_vel_pos_z"]*timestep)**2)**0.5
                )
            )    
        
        # Calculate cumulative sum of displacement
        output_df['total_cartesian_distance'] = output_df['cartesian_displacement'].cumsum()

        return output_df, output_metadata
    
    def _cumulative_rotational_distance(self, output_df: pd.DataFrame, output_metadata: Dict):
        timestep = output_metadata["fundamental_kinematics_metadata"]["avg_timestep"]
    
        # Caculate displacement for every timestep
        output_df = output_df.assign(
                rotational_displacement=lambda x: (
                    ((x["head_vel_rot_i"]*timestep)**2 +  \
                      (x["head_vel_rot_j"]*timestep)**2 +  \
                        (x["head_vel_rot_k"]*timestep)**2 + \
                           (x["head_vel_rot_l"]*timestep)**2 \
                            )**0.5
                )
            )    
        
        # Calculate cumulative sum of displacement
        output_df['total_rotational_distance'] = output_df['rotational_displacement'].cumsum()

        return output_df, output_metadata
