import json
import pandas as pd
import pathlib


class CollectiveBodyDataManager:

    def __init__(self, database_directory, metrics_directory = None):
        # Save databaste and metrics paths; if no separate metrics path, default to database
        if metrics_directory is None:
            metrics_directory = database_directory
        self.database_directory = pathlib.Path(database_directory)
        self.metrics_directory = pathlib.Path(metrics_directory)
        self.raw_movement_database_path = self.database_directory / "raw_movement_database.csv"
        self.movement_metrics_path= self.metrics_directory / "algorithm_movement_metrics.csv"
        self.alogirthm_metric_summary_path = self.metrics_directory / "algorithm_metric_summary_statistics.json"

        # Load datasets and metrics
        self.raw_movement_df = self._load_database()
        self.algorithm_metrics_df = self._load_algorithm_metrics()
        self.metrics_summaries_dict, self.metrics_options_list = self._load_metrics_options()

    def get_session_IDs(self):
        return sorted(list(self.raw_movement_df["session_number"].unique()))
    
    def get_actor_IDs(self, session_num):
        loaded_dataset = self.raw_movement_df.loc[(self.raw_movement_df["session_number"] == int(session_num))]
        return sorted(list(loaded_dataset["headset_number"].unique()))
    
    def get_metric_options(self):
        return self.metrics_options_list

    def get_loaded_dataset(self):
        return sorted(list(self.raw_movement_df))
    
    def get_frame_dataset_dict(self, session_num, actor_num, chapter_num, normalize=True):
        dataset_dict = {}


        dataset_df = self._get_single_dataset(session_num, actor_num, chapter_num)

        if normalize:
            for col_val in dataset_df.columns:
                if "_pos_" in col_val or "_rot_" in col_val:
                    dataset_df[col_val]=(dataset_df[col_val] - dataset_df[col_val].min()) / (dataset_df[col_val].max() - dataset_df[col_val].min())

                    '''
                    min_val = dataset_df[col_val].min()
                    dataset_df[col_val].apply(lambda x: x-min_val)
                    max_val = dataset_df[col_val].max()
                    dataset_df[col_val].apply(lambda x: x/max_val)'''

        # Populate and return dictionary
        dataset_dict["session_num"] = session_num
        dataset_dict["headset_num"] = actor_num
        dataset_dict["normalized"] = normalize
        dataset_dict["dataset"] = dataset_df

        return dataset_dict     
    
    def get_metric_summary_statistics(self):
        # TODO - implement metric selection
        pass    
    
    def get_chosen_metric(self, metric_key):
        return self.algorithm_metrics_df[["data_collect_name", metric_key]]

    def _load_database(self):
        self._log_output(f"Loading database at path {self.raw_movement_database_path}")
        raw_movement_df = pd.read_csv(self.raw_movement_database_path)
        self._log_output(f"Database load completed with {len(raw_movement_df)} entries")
        return raw_movement_df

    def _load_algorithm_metrics(self):
        self._log_output(f"Loading metrics at path {self.movement_metrics_path}")
        alogirthm_metrics_df = pd.read_csv(self.movement_metrics_path)
        self._log_output(f"Database load completed with {len(alogirthm_metrics_df)} entries")
        return alogirthm_metrics_df


    def _load_metrics_options(self):
        self._log_output("Loading metric options")
        
        # Load metrics options
        with open(self.alogirthm_metric_summary_path) as json_file:
            algorithm_metric_statistics = json.load(json_file)

        options_keys = algorithm_metric_statistics.keys()

        return algorithm_metric_statistics, options_keys


    def _get_single_dataset(self, session_num, actor_num, chapter_num):

        self._log_output(f"Loading chapter {chapter_num} session number {session_num} with headset number {actor_num}")

        loaded_dataset = self.raw_movement_df.loc[
            (self.raw_movement_df["session_number"] == int(session_num)) & 
            (self.raw_movement_df["headset_number"] == int(actor_num)) & 
            (self.raw_movement_df["chapitre"] == int(chapter_num))]
        self._log_output(f"Single dataset loaded with {len(loaded_dataset)} entries")

        return loaded_dataset

    def get_single_metric(self, session_num, actor_num, metric_key):
        selected_metric_df = self.raw_movement_df.loc[
            (self.algorithm_metrics_df["session_number"] == int(session_num)) & 
            (self.algorithm_metrics_df["headset_number"] == int(actor_num)) & 
            (self.algorithm_metrics_df["headset_number"] == int(actor_num))]
        
        return selected_metric_df[[metric_key]]

    def _log_output(self, to_output):
        print(f"{__class__.__name__}: {to_output}")