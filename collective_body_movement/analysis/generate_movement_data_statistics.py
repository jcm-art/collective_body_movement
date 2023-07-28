import pandas as pd
import pathlib
import numpy as np

class CollectiveBodyMovementDataStatistics:

    def __init__(self, movement_database_path, statistics_output_path) -> None:
        self.movement_database_path = pathlib.Path(movement_database_path)
        self.statistics_output_path = pathlib.Path(statistics_output_path)

        # Read database
        self.raw_movement_df = pd.read_csv(self.movement_database_path, index_col=0)

        # Create output database
        self.movement_statistics_df = pd.DataFrame()

    def generate_statistics_database(self):
        
        # Get all unique data collections in the database
        self._get_datacollect_list()

        all_statistics_dict = {}

        # Iterate through each data collection
        for data_collect_name in self.data_collect_list:
            # Get a dataframe for each data collection
            single_df = self._get_single_dataframe(data_collect_name)

            # Generate statistics for each data collection
            statistics_dict = self._generate_basic_statistics(single_df,data_collect_name)
            statistics_dict = self._add_advanced_statistics(single_df, statistics_dict)

            # Append statistics to overall statistics dictionary
            all_statistics_dict[data_collect_name] = statistics_dict

        # Convert dictionary to dataframe
        formatted_dict = {}
        for k, v in all_statistics_dict.items():

            for k2, v2 in v.items():
                if k2 in formatted_dict:
                    formatted_dict[k2].append(v2)
                else:
                    formatted_dict[k2] = [v2]

        self.movement_statistics_df = pd.DataFrame.from_dict(formatted_dict)

    def save_statistics_df(self):
        self._log_output("Saving raw database and skipped file information")
        self.statistics_output_path.parent.mkdir(parents=True, exist_ok=True)  
        self.movement_statistics_df.to_csv(self.statistics_output_path)  


    def _generate_basic_statistics(self, single_df, data_collect_name):
        # Available fields in raw movement database:
        # ,time,chapitre,leftballscount,rightballscount,
        # headpos_x,headpos_y,headpos_z,
        # leftpos_x,leftpos_y,leftpos_z,rightpos_x,rightpos_y,rightpos_z,
        # bigballpos_x,bigballpos_y,bigballpos_z,headRot_i,
        # headRot_j,headRot_k,headRot_l,
        # leftrot_i,leftrot_j,leftrot_k,leftrot_l,
        # rightpos1_i,rightpos1_j,rightpos1_k,rightpos1_l,
        # data_collection_name,subfolder,data_collection_example,client_number,
        # datafile_year,datafile_day,datafile_month,datafile_seconds,timestamp,timestamp_from_start

        # TODO - replace dataframe with dictionary to improve speed
        single_stats_dict = {}
        # single_stats_df = pd.DataFrame([data_collect_name], columns=['data_collect_name'])
        single_stats_dict['data_collect_name'] = data_collect_name

        sensor_locations = ['head','left','right','bigball']
        motion_types = ['pos','rot']
        pos_axes = ['x','y','z']
        rot_axes = ['i','j','k','l']

        time_array = single_df['timestamp_from_start'].to_numpy()
        time_step = (np.max(time_array)-np.min(time_array))/len(time_array) * 10**-9

        for sensor_location in sensor_locations:
            for motion_type in motion_types:
                if motion_type == 'pos':
                    motion_axes = pos_axes
                elif motion_type == 'rot':
                    motion_axes = rot_axes
                
                # Skip ball rotation, no data provided
                if motion_type == 'rot' and sensor_location == 'bigball':
                    continue
                else:
                    for axes in motion_axes:
                        data_array = single_df[sensor_location + '_' + motion_type + '_' + axes].to_numpy()
                        normalized_array = data_array - np.mean(data_array)

                        # TODO - replace with dictionary of functions
                        derived_val = 'mean'
                        new_column = sensor_location + '_' + motion_type + '_' + axes + '_' + derived_val
                        statistic = np.mean(data_array)
                        single_stats_dict[new_column] = statistic if statistic else np.nan

                        derived_val = 'std'
                        new_column = sensor_location + '_' + motion_type + '_' + axes + '_' + derived_val
                        statistic = np.std(data_array)
                        single_stats_dict[new_column] = statistic if statistic else np.nan

                        # Spread data
                        derived_val = 'normalized_max'
                        new_column = sensor_location + '_' + motion_type + '_' + axes + '_' + derived_val
                        norm_max_statistic = np.max(normalized_array)
                        single_stats_dict[new_column] = norm_max_statistic if norm_max_statistic else np.nan

                        derived_val = 'normalized_min'
                        new_column = sensor_location + '_' + motion_type + '_' + axes + '_' + derived_val
                        norm_min_statistic = np.min(normalized_array)
                        single_stats_dict[new_column] = norm_min_statistic if norm_min_statistic else np.nan

                        derived_val = 'range'
                        new_column = sensor_location + '_' + motion_type + '_' + axes + '_' + derived_val
                        range_statistic = norm_max_statistic-norm_min_statistic
                        single_stats_dict[new_column] = range_statistic if range_statistic else np.nan

                        # Derivative data
                        derived_val = 'speed_mean'
                        derivative_array = np.diff(data_array)/time_step

                        new_column = sensor_location + '_' + motion_type + '_' + axes + '_' + derived_val
                        statistic = np.mean(derivative_array)
                        single_stats_dict[new_column] = statistic if statistic else np.nan

                        derived_val = 'speed_std'
                        new_column = sensor_location + '_' + motion_type + '_' + axes + '_' + derived_val
                        statistic = np.std(derivative_array)
                        single_stats_dict[new_column] = statistic if statistic else np.nan

                        # Spread derivative data
                        derived_val = 'max_speed'
                        new_column = sensor_location + '_' + motion_type + '_' + axes + '_' + derived_val
                        norm_max_statistic = np.max(derivative_array)
                        single_stats_dict[new_column] = norm_max_statistic if norm_max_statistic else np.nan

                        derived_val = 'min_speed'
                        new_column = sensor_location + '_' + motion_type + '_' + axes + '_' + derived_val
                        norm_min_statistic = np.min(derivative_array)
                        single_stats_dict[new_column] = norm_min_statistic if norm_min_statistic else np.nan

                        derived_val = 'range_speed'
                        new_column = sensor_location + '_' + motion_type + '_' + axes + '_' + derived_val
                        range_statistic = norm_max_statistic-norm_min_statistic
                        single_stats_dict[new_column] = range_statistic if range_statistic else np.nan

        return single_stats_dict

    def _add_advanced_statistics(self, single_df, statistics_dict):
        x_array = single_df['head_pos_x'].to_numpy()
        y_array = single_df['head_pos_y'].to_numpy()
        z_array = single_df['head_pos_z'].to_numpy()

        total_distance_traveled = 0

        for i in range(len(x_array)-1):
            total_distance_traveled += np.sqrt((x_array[i+1]-x_array[i])**2 + (y_array[i+1]-y_array[i])**2 + (z_array[i+1]-z_array[i])**2)

        statistics_dict["total_distance_traveled"] = total_distance_traveled

        return statistics_dict

    def _get_datacollect_list(self):
        self.data_collect_list = self.raw_movement_df['data_collection_example'].unique()

    def _get_single_dataframe(self,data_collect_name):
        single_df = self.raw_movement_df.loc[self.raw_movement_df['data_collection_example'] == data_collect_name]
        return single_df

    def _log_output(self, to_output):
        print(f"{__class__.__name__}: {to_output}") 

if __name__ == "__main__":
    cbmds = CollectiveBodyMovementDataStatistics(
        movement_database_path="data/movement_database/raw_movement_database.csv",
        statistics_output_path="data/movement_database/movement_statistics_database.csv")
    cbmds.generate_statistics_database()
    cbmds.save_statistics_df()