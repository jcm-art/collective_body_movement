
import os

import pandas as pd
import pathlib

import streamlit as st


class MovementDataManager:

    def __init__(self) -> None:
        self.dataset_ids =[]
        #self.headset_num_dict = {}
        self.movement_df_dict = {}

    def load_movement_data_from_upload(_self):
        # Get Uploaded files
        print("Initiaing file uploader")
        movement_file_list = st.file_uploader("Upload raw data movement file", type=["csv"], accept_multiple_files=True)
        _self._load_file_list(movement_file_list)
    
    def load_local_movement_data_from_filepath(_self, _movement_file_directory):
        
        movement_file_list = _self._get_discovered_filepaths(_movement_file_directory)

        print(movement_file_list)

        _self._load_file_list(movement_file_list)

    def _get_discovered_filepaths(self, directory_root: str):
        input_path = pathlib.Path(directory_root)
        filepaths_in_directory = self._get_data_paths(input_path, ".csv")

        return filepaths_in_directory
    
    def _get_data_paths(self, filepath, filetype):
        paths = []
        for root, dirs, files in os.walk(filepath):
            for file in files:
                if file.lower().endswith(filetype.lower()):
                    paths.append(str(pathlib.PurePath(root, file)))
        
        return paths

    def _load_file_list(self, df_file_path_list):
        for file in df_file_path_list:
            movement_df = pd.read_csv(file)
            dataset_id = list(movement_df["dataset_id"].unique())[0]
            self.dataset_ids.append(dataset_id)
            #print(dataset_id)

            self.movement_df_dict[dataset_id] = movement_df
            #self.headset_num_dict[dataset_id] = list(movement_df["headset_number"].unique())
        
            #print(self.headset_num_dict[dataset_id])

    def get_dataset_IDs(self):
        return self.dataset_ids

    def get_actor_IDs(self, dataset_id: int):
        pass
        #return self.headset_num_dict[dataset_id]
        # TODO - fix bug with some csvs missing headset number


    def get_updated_dataframe(self, user_dataset_selection, user_chapter_selection_static):
        # TODO(jcm-art): enable multiple dataset comparison
        selected_dataset = self.movement_df_dict[user_dataset_selection[0]]
        return selected_dataset[selected_dataset["chapitre"]==user_chapter_selection_static]