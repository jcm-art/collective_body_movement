import os
import pathlib
import pandas as pd
import numpy as np


class CollectiveBodyDataCleaner:

    def __init__(self, input_path, output_path="/data/cleaned/") -> None:
        # Initialize input and output
        self.input_path = pathlib.Path(input_path)
        self.output_directory = pathlib.Path(output_path)
        self.output_path = self.output_directory /'raw_movement_database.csv'
        self.skipped_output_path = self.output_directory /'raw_movement_skipped_database.csv'
        self._log_output(f"Input path: {self.input_path}")
        self._log_output(f"Output path: {self.output_directory}")

        # Get Filepaths
        self.paths = []
        self.session_counter = 0
        self._get_data_paths(self.input_path, ".csv")
        self.session_numbers = {}

        # Import Data
        self.movementdf = pd.DataFrame()
        self.skippeddf = pd.DataFrame(columns=['dataset_path','num_entries','reason_skipped'])

    def import_data(self,fast_debug=False, fast_debug_limit=10):
        counter = 0

        for path in self.paths:
            if fast_debug and counter > fast_debug_limit:
                continue
            else:
                single_df = pd.read_csv(path, skiprows=1, delimiter=";",names=[
                    "time","head_pos","left_pos","right_pos","head_rot","left_rot","right_rot","chapitre","bigball_pos","leftballscount","rightballscount"
                ])  ## pandas as pd

                row, _ = single_df.shape
                if row <=2:
                    self._log_output(f"Skipping {path}, no data provided")
                    self.skippeddf.loc[len(self.skippeddf.index)] = [path, row, "Datafile is empty"] 
                    continue
                else:
                    self._log_output(f"Adding {path} to dataframe.")
                    # Clean Dataframe
                    single_df = self._clean_dataframe(single_df)
                    single_df = self._add_metadata(single_df,path)
                    
                    # Add to overall dataframe
                    self.movementdf = pd.concat([self.movementdf, single_df], ignore_index=True)
            counter += 1

    def save_clean_data(self):
        self._log_output("Saving raw database and skipped file information")
        self.output_path.parent.mkdir(parents=True, exist_ok=True)  
        self.movementdf.to_csv(self.output_path)  
        self.skippeddf.to_csv(self.skipped_output_path)  

    def _get_data_paths(self, filepath, filetype):
        for root, dirs, files in os.walk(filepath):
            for file in files:
                if file.lower().endswith(filetype.lower()):
                    self.paths.append(pathlib.PurePath(root, file))

    def _clean_dataframe(self, df):
        # Remove incorrect header rows and missing data
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
        
        return df

    def _add_metadata(self, df, path):
        # Get data aquisition and time labels
        # TODO - currently hardcoded, could cause issues with future data collections if structure changes
        data_collection_name = path.parts[2]
        subfolder = "_".join(path.parts[3:-1])
        csv_file = path.parts[-1]
        headset_number = int(path.name.split("+")[2][0])
        date_time_str = path.name.split("_")[-1][:-4]
        data_year = int(date_time_str.split("-")[0])
        data_day = int(date_time_str.split("-")[1])
        data_month = int(date_time_str.split("-")[2])
        data_hour = int(date_time_str.split("-")[4])
        data_minute = int(date_time_str.split("-")[5])
        data_second = int(date_time_str.split("-")[6])

        


        # Add metadata to dataframe
        df["file_name"] = data_collection_name
        df["subfolder"] = subfolder
        df["data_collection_example"] = csv_file
        df["headset_number"] = headset_number
        df["datafile_year"] = data_year
        df["datafile_day"] = data_day
        df["datafile_month"] = data_month
        df["datafile_seconds"] = data_hour*24+data_minute*60+data_second

        # Convert time to datetime
        df["time"] =df["datafile_year"].apply(str)+ ":" + df["datafile_month"].apply(str)+ ":" + df["datafile_day"].apply(str)+ ":" + df["time"]
        df["time"] = pd.to_datetime(df["time"], format='%Y:%m:%d:%H:%M::%S:%f')
        df["timestamp"] = df.time.values.astype(np.int64) ** 10
        start_time = df["timestamp"].min()
        df["timestamp_from_start"] = df["timestamp"] - start_time

        session_number = self._get_session_number(start_time)
        df["data_collection_session_inferred"] = session_number

        return df

    def _get_session_number(self, start_time, threshold=100):
        '''Method to infer the session number based on the start time of the data collection. The
        threshold value gives a margin to account for different start times.'''

        if bool(self.session_numbers)==False:
            self.session_numbers[self.session_counter] = start_time
            self.session_counter += 1
            return self.session_counter-1

        # Check dictionary for start time to see if session already exists
        for key, value in self.session_numbers.items():
            if abs(value - start_time) < threshold:
                return key
            else:
                self.session_numbers[self.session_counter] = start_time
                self.session_counter += 1
                return self.session_counter-1


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

    cbdc = CollectiveBodyDataCleaner(
        input_path="bin/data/DATA.2023.06.26/",
        output_path="data/movement_database/")
    
    cbdc.import_data(fast_debug=True, fast_debug_limit=10)
    cbdc.save_clean_data()