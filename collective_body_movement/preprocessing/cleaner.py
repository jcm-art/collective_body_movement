# Collective Body Movement Application
# Director: Sarah Silverblatt-Buser (https://www.sarahsilverblatt.com/)
# Author: Justin Martin (jcm-art)

import datetime
import os
import numpy as np
import pathlib
import pandas as pd
from typing import Dict, List

from ..utils import CollectiveBodyLogger, CollectiveBodyBolt

class DataSummary:

    def __init__(self,dataset_id, data_path = None):
        self.data_path_dict = {
            'dataset_id': dataset_id,
            'headset_number': None,
            'session_number_path': None,
            'session_number_data': None,
            'path_datetime': None,
            'path_abstime': None,
            'data_start_datetime': None,
            'data_start_abstime': None,
            'is_valid': None,
            'error_codes': None,
            'num_frames': None,
            'elapsed_time': None,
            'chapter_1': None,
            'chapter_2': None,
            'chapter_3': None,
            'chapter_4': None,
            'data_collection': None, # Upload time / data collection event
            'data_source': None, # Server or headset
            'data_path': data_path, # Path to data file
        }

    def set_data_parameter(self, field, new_value):
        if field in self.data_path_dict:
            if field == "error_codes" and self.data_path_dict["error_codes"] is not None:
                self.data_path_dict[field] = self.data_path_dict[field] + f", {new_value}"
            else:
                self.data_path_dict[field] = new_value
        else:
            raise Exception(f"Field {field} is not in the dictionary for {self.__class__.__name__}")

    def get_data_parameter(self, field):
        if field in self.data_path_dict:
            return self.data_path_dict[field]
        else:
            raise Exception(f"Field {field} is not in the dictionary for {self.__class__.__name__}")

    def get_data_path_dict(self):
        return self.data_path_dict

class DataCleanerBolt(CollectiveBodyBolt):

    def __init__(
            self, 
            output_directory_path: str, 
            save_intermediate_output: bool, 
            fast_debug: bool=False, 
            fast_debug_limit: int=10) -> None:
        # Initialize template class
        super().__init__(output_directory_path, save_intermediate_output)
        self.fast_debug = fast_debug
        self.fast_debug_limit = fast_debug_limit

        # Initialize logger
        self.logger = CollectiveBodyLogger(__class__.__name__)


        # Initialize session tracking
        self.path_session_counter = 0
        self.path_session_numbers = {}
        self.data_session_counter = 0
        self.data_session_numbers = {}

    def process(
        self, 
        input_dataframe_list: List[pd.DataFrame], 
        aggregate_metadata: Dict,
        input_metadata_list: List[Dict]
     ) -> (List[pd.DataFrame], List[Dict]):
        """"Process functiont to take a metadata disctionary with file paths and
        preprocess and clean them."""
        self.output_df_list = input_dataframe_list
        self.aggregate_metadata_output = aggregate_metadata
        self.output_metadata_list = input_metadata_list

        # Extract pipeline information from aggregate metadata
        discovered_filepaths = self.aggregate_metadata_output['input_metadata']['discovered_filepaths']
        quick_debug_mode = self.aggregate_metadata_output['input_metadata']['quick_debug_mode']
        ingest_limit = self.aggregate_metadata_output['input_metadata']['file_ingest_limit']

        df_list, metadata_list = self._load_data_from_file_paths(
            discovered_filepaths, quick_debug_mode, ingest_limit
        )

        # TODO - add cleaning information to aggregate metadata

        for df, metadata in zip(df_list,metadata_list):
            dataset_id = metadata["dataset_id"]
            dataset_output_metadata =  {
                dataset_id: {
                    'cleaned_metadata': metadata,
                }
            }
            self.output_metadata_list.append(dataset_output_metadata)
            self.output_df_list.append(df)

        if self.save_intermediate_output:
            self.save_output()

        return self.output_df_list, self.aggregate_metadata_output, self.output_metadata_list

    def _load_data_from_file_paths(
            self, 
            paths: List[pathlib.Path], 
            fast_debug: bool=False, 
            fast_debug_limit: int=10
    ):
        dataset_id = 0
        data_frame_list = []
        metadata_list = []

        for pathname in paths:
            path = pathlib.Path(pathname)

            # Initialize Data Summary class
            data_summary = DataSummary(dataset_id,path)

            # Generate Metadata from path
            data_summary = self._append_path_name_metadata(path, data_summary)

            # Read CSV file 
            data_df = self._read_csv_to_dataframe(path)

            # Skip full data ingest if fast debug in usage
            if fast_debug and dataset_id > fast_debug_limit:
                # For Quick Debugging, run only quick validation to check file length
                data_summary, data_df = self._length_validation(data_summary, data_df)
            else:
                data_summary, data_df = self._import_movement_data(path, data_df, data_summary)

            # Add data summary to list 
            # TODO - leave as data summary class
            metadata_list.append(data_summary.get_data_path_dict())
            data_frame_list.append(data_df)

            dataset_id += 1

            if fast_debug and dataset_id > fast_debug_limit:
                return data_frame_list, metadata_list

        return data_frame_list, metadata_list

    # TODO - remove
    def load_data_from_file_paths(self, filepath_metadata: Dict, fast_debug: bool=False, fast_debug_limit: int=10):
        dataset_id = 0

        paths = filepath_metadata["initial_file_paths"]

        for path in paths:

            # Initialize Data Summary class
            data_summary = DataSummary(dataset_id,path)

            # Generate Metadata from path
            data_summary = self._append_path_name_metadata(path, data_summary)

            # Read CSV file 
            data_df = self._read_csv_to_dataframe(path)

            # Skip full data ingest if fast debug in usage
            if fast_debug and dataset_id > fast_debug_limit:
                # For Quick Debugging, run only quick validation to check file length
                data_summary, data_df = self._length_validation(data_summary, data_df)
            else:
                data_summary, data_df = self._import_movement_data(path, data_df, data_summary)

            # Add data summary to list 
            self.data_summaries.append(data_summary.get_data_path_dict())

            dataset_id += 1

    def _append_path_name_metadata(self, path, data_summary) -> DataSummary:
        # Extract data aquisition and time labels
        # TODO - currently hardcoded, could cause issues with future data collections if structure changes
        data_collection_name = path.parts[2]
        subfolder = "_".join(path.parts[3:-1])
        headset_number = int(path.name.split("+")[2][0])
        date_time_str = path.name.split("_")[-1][:-4]
        data_year = int(date_time_str.split("-")[0])
        data_day = int(date_time_str.split("-")[1])
        data_month = int(date_time_str.split("-")[2])
        data_hour = int(date_time_str.split("-")[4])
        data_minute = int(date_time_str.split("-")[5])
        data_second = int(date_time_str.split("-")[6])

        path_datetime = datetime.datetime(data_year,data_month,data_day,data_hour,data_minute,data_second)

        # Update data summary class timing information
        data_summary.set_data_parameter('path_datetime', path_datetime)
        data_summary.set_data_parameter('path_abstime', path_datetime.timestamp())

        # Update data summary class data source information
        data_source = "no data source found"
        if "headset" in subfolder.lower():
            data_source = "headset"
        elif "server" in subfolder.lower():
            data_source = "server"
        data_summary.set_data_parameter('data_source', data_source)

        # Update data summary class data collection information
        data_summary.set_data_parameter('data_collection', data_collection_name)

        # Update data summary class data headset number
        data_summary.set_data_parameter('headset_number', headset_number)

        # Determine session number based on path datetime
        session_number = self._get_path_session_number(path_datetime)
        data_summary.set_data_parameter('session_number_path', session_number)

        return data_summary 

    def _append_datafile_metadata(self, path, data_df, data_summary) -> DataSummary:
        # TODO - implement metadata extraction from data file

        # Get datetime from path name
        dt_start_time = data_df['time'].min()
        abs_start_time = data_df['timestamp'].min()
        abs_end_time = data_df['timestamp'].max()
        abs_elapsed_time = abs_end_time - abs_start_time

        # Update data summary class timing information
        data_summary.set_data_parameter('data_start_datetime', dt_start_time)
        data_summary.set_data_parameter('data_start_abstime', abs_start_time)
        data_summary.set_data_parameter('elapsed_time', abs_elapsed_time)

        # Check chapters
        unique_chapters = data_df['chapitre'].unique()
        chapter_1_present = False
        chapter_2_present = False
        chapter_3_present = False
        chapter_4_present = False

        if 1 in unique_chapters:
            chapter_1_present = True
        if 2 in unique_chapters:
            chapter_2_present = True
        if 3 in unique_chapters:
            chapter_3_present = True
        if 4 in unique_chapters:
            chapter_4_present = True

        data_summary.set_data_parameter('chapter_1', chapter_1_present)
        data_summary.set_data_parameter('chapter_2', chapter_2_present)
        data_summary.set_data_parameter('chapter_3', chapter_3_present)
        data_summary.set_data_parameter('chapter_4', chapter_4_present)

        # Note that chapter 4 not being present doesn't force a failure
        if (chapter_1_present and chapter_2_present and chapter_3_present) == False:
            data_summary.set_data_parameter('is_valid', False)
            data_summary.set_data_parameter('error_codes', "Missing chapters")

        if tuple(unique_chapters) != (1,2,3,4):
            data_summary.set_data_parameter('is_valid', False)
            data_summary.set_data_parameter('error_codes', "Too many chapters")

        # Get session number from data file
        session_number = self._get_data_session_number(abs_start_time)
        data_summary.set_data_parameter('session_number_data', session_number)

        return data_summary 


    def _import_movement_data(self, path, data_df, data_summary):
        # Run pre-validation on dataframe
        data_summary = self._pre_validate_dataframe(data_df, data_summary)

        # Check if dataframe is valid
        if data_summary.get_data_parameter("is_valid") == False:
            self._log_output(f"Skipping {path}, no data provided")
            return data_summary, data_df
        else:
            self._log_output(f"Checking {path} for dataframe.")
            # Clean Dataframe
            data_df = self._clean_dataframe(data_df, data_summary)

            # Append extracted metadata to data summary from datafile
            data_summary = self._append_datafile_metadata(path, data_df, data_summary)

            # Check cleaned data
            # TODO - passs in data summary to check cleaned data
            valid_dataframe, error_codes = self._post_validate_dataframe(data_df)    

            if valid_dataframe == False:
                self._log_output(f"Skipping {path}, invalida data fround")
                data_summary.set_data_parameter("is_valid", False)
                data_summary.set_data_parameter("error_codes", error_codes)
                return data_summary, data_df

        # Add to overall dataframe
        self._log_output(f"{path} cleaning and processing completed.")
        return data_summary, data_df

    def _read_csv_to_dataframe(self, path):
        # Read dataframe from csv path
        single_df = pd.read_csv(path, skiprows=1, delimiter=";",names=[
            "time","head_pos","left_pos","right_pos","head_rot","left_rot","right_rot","chapitre","bigball_pos","leftballscount","rightballscount"
        ])

        return single_df


    def _length_validation(self, data_summary, data_df):
        num_lines = len(data_df)

        # Check size of dataframe
        if num_lines <= 2:
            data_summary.set_data_parameter('is_valid', False)
            data_summary.set_data_parameter('error_codes', "empty_dataset")
        elif num_lines <= 1000:
            data_summary.set_data_parameter('is_valid', False)
            data_summary.set_data_parameter('error_codes', "short_dataset_expected_restart")
        else:        
            data_summary.set_data_parameter('is_valid', True)
            data_summary.set_data_parameter('error_codes', "non_empty_dataset")

        data_summary.set_data_parameter('num_frames', num_lines-1)
        
        return data_summary
                    

    def _pre_validate_dataframe(self, data_df, data_summary):
        # TODO - other pre-validation checks
        data_summary = self._length_validation(data_summary, data_df)

        # Flag headset data as invalid
        if data_summary.get_data_parameter('data_source') == "headset":
            data_summary.set_data_parameter('is_valid', False)
            data_summary.set_data_parameter('error_codes', "headset_data_expected_not_valid")

        return data_summary
    
    def _post_validate_dataframe(self, df):
        
        # CHeck position values are within expected range
        distance_threshold = 0.1
        cartesian_dimensions = ['x','y','z']
        sensor_types = ['head_pos','left_pos','right_pos']
        for sensor in sensor_types:
            for dimension in cartesian_dimensions:
                target_column = f"{sensor}_{dimension}"
                if df[target_column].max() - df[target_column].min() < distance_threshold:
                    return False, f"{sensor} dimension {dimension} value range is too small"

        return True, None
    
    def _post_ingest_validation(self):
        # TODO - implement check for single data source in session
        pass

    def _clean_dataframe(self, df, data_summary):
        # Remove incorrect header rows and missing data
        df['dataset_id'] = data_summary.get_data_parameter('dataset_id')
        df['headset_number'] = data_summary.get_data_parameter('headset_number')
        df['session_number'] = data_summary.get_data_parameter('session_number_path')
        df = df.dropna()
        df = df.reset_index(drop=True)

        # Expand text columns - tranlation
        df = self._strip_split_columns(df, 
                                       column_list=['head_pos','left_pos','right_pos','bigball_pos'],
                                       dimensions =['x','y','z'],
                                       remove_vals=["(",")"," "])
        
        # Expand text columns - rotation
        df = self._strip_split_columns(df, 
                                       column_list=['head_rot','left_rot','right_rot'],
                                       dimensions =['i','j','k','l'],
                                       remove_vals=["(",")"," "])
        
        # Convert time to datetime
        path_datetime = data_summary.get_data_parameter("path_datetime")
        time_df = pd.DataFrame()
        time_df['time'] = pd.to_datetime(df['time'], format="%H:%M::%S:%f")

        time_df['year'] = path_datetime.year
        time_df['month'] = path_datetime.month
        time_df['day'] = path_datetime.day
        time_df['hour'] = time_df['time'].dt.hour
        time_df['minute'] = time_df['time'].dt.minute
        time_df['second'] = time_df['time'].dt.second
        time_df['microsecond'] = time_df['time'].dt.microsecond
        time_df = time_df.drop(['time'], axis=1)
        time_df = pd.to_datetime(time_df)
        
        # Set time values including elapsed time
        df['time'] = pd.to_datetime(time_df)
        df['timestamp'] = df['time'].values.astype(np.int64) // 10 ** 6 # Get time in miliseconds
        start_time = df['timestamp'].min()
        df['elapsed_time'] = df['time'].values.astype(np.int64) // 10 ** 6 - start_time

        return df

    def _get_path_session_number(self, path_datetime, threshold=500):
        '''Method to infer the session number based on the start time of the data collection. The
        threshold value gives a margin to account for different start times. This method is based
        on the datetime provided by the file path.'''

        if bool(self.path_session_numbers)==False:
            self.path_session_numbers[self.path_session_counter] = path_datetime.timestamp()
            self.path_session_counter += 1
            return self.path_session_counter-1

        # Check dictionary for start time to see if session already exists
        for key, value in self.path_session_numbers.items():
            timedelta_val = path_datetime.timestamp() - value
            if abs(timedelta_val) < threshold:
                return key
        
        # If session is not found, create new session in dictionary and return the key
        self.path_session_numbers[self.path_session_counter] = path_datetime.timestamp()
        self.path_session_counter += 1
        return self.path_session_counter-1

    def _get_data_session_number(self, start_time, threshold=500):
        '''Method to infer the session number based on the start time of the data collection. The
        threshold value gives a margin to account for different start times.'''
        # TODO - fix to use datetime

        if bool(self.data_session_numbers)==False:
            self.data_session_numbers[self.data_session_counter] = start_time
            self.data_session_counter += 1
            return self.data_session_counter-1

        # Check dictionary for start time to see if session already exists
        for key, value in self.data_session_numbers.items():
            if abs(value - start_time) < threshold:
                return key
            else:
                self.data_session_numbers[self.data_session_counter] = start_time
                self.data_session_counter += 1
                return self.data_session_counter-1


    def _strip_split_columns(self, df,column_list, dimensions, remove_vals=["(",")"," "]):

        for column in column_list:
            column_list = [column  + "_" + d for d in dimensions]
            for val in remove_vals:
                df[column] = df[column].str.replace(val,'')
            
            df[column_list] = df[column].str.split(',',expand=True).astype(float)
            df = df.drop([column], axis=1)

        return df

    def _inspect_dataframe(self, dataframe):
            self._log_output(f"Data frame head:\n{dataframe.head()}")
            self._log_output(f"Data frame description:\n{dataframe.describe()}")
            self._log_output(f"Data frame datatypes:\n{dataframe.dtypes}")
            self._log_output(f"Time:\n{dataframe['time']}")

    def _log_output(self, output):
        print(f"{__class__.__name__}: {output}")



if __name__ == "__main__":
    print("Running data cleaning and import for headset and server data.")

    cbdc = DataCleanerBolt(
        input_path="bin/data/DATA.2023.06.26/",
        output_path="data/movement_database/")
    
    cbdc.import_data(fast_debug=True, fast_debug_limit=10)
    cbdc.save_clean_data()