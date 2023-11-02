

import pandas as pd

import streamlit as st


from collective_body_movement.ingest.directory_ingest import DirectoryParserBolt


class MovementDataManager:

    def __init__(self) -> None:
        self.dataset_ids =[]
        #self.headset_num_dict = {}
        self.movement_df_dict = {}

    def load_movement_data_from_upload(_self):
        # Get Uploaded files
        movement_file_list = st.file_uploader("Upload raw data movement file", type=["csv"], accept_multiple_files=True)
        _self._load_file_list(movement_file_list)
    
    def load_local_movement_data_from_filepath(_self, _movement_file_directory):
        
        # User directory parsing bolt to find files
        dpb = DirectoryParserBolt("~/tmp", False)

        # Data input metadata
        input_metadata = {
            "input_metadata": {
                "directory_root_path": _movement_file_directory,
                "quick_debug_mode": False,
                "file_ingest_limit": None,
            }
        }

        _, filepath_metadata, _ = dpb.process(None, input_metadata, None)

        print(filepath_metadata)

        movement_file_list = filepath_metadata['input_metadata']['discovered_filepaths']

        print(movement_file_list)

        _self._load_file_list(movement_file_list)

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
        selected_dataset = self.movement_df_dict[user_dataset_selection]
        return selected_dataset[selected_dataset["chapitre"]==user_chapter_selection_static]