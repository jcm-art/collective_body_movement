import pandas as pd
import pathlib
import numpy as np
import json

class CollectiveBodyMovementDataStatistics:

    def __init__(self, movement_database_path, statistics_output_path) -> None:
        # Initailzie paths
        self.movement_database_path = pathlib.Path(movement_database_path)
        self.movement_database_path = self.movement_database_path/"raw_movement_database.csv"
        self.statistics_output_dir_path = pathlib.Path(statistics_output_path)
        self.basic_metrics_output_path = pathlib.Path(self.statistics_output_dir_path/"basic_movement_metrics.csv")
        self.algorithm_metrics_output_path = pathlib.Path(self.statistics_output_dir_path/"algorithm_movement_metrics.csv")
        self.basic_metric_stats_output_path = pathlib.Path(self.statistics_output_dir_path/"basic_metric_summary_statistics.json")
        self.algorithm_metric_stats_output_path = pathlib.Path(self.statistics_output_dir_path/"algorithm_metric_summary_statistics.json")
        self.metric_stats_df_output_path = pathlib.Path(self.statistics_output_dir_path/"all_metric_summary_statistics.csv")
        
        # Make directory if not available
        self.statistics_output_dir_path.mkdir(parents=True, exist_ok=True)

        # Read database
        self.raw_movement_df = pd.read_csv(self.movement_database_path, index_col=0)

        # Create output database
        self.basic_movement_metrics_df = pd.DataFrame()
        self.algorithm_movement_metrics_df = pd.DataFrame()

        # Create output summary dictionary for json file and metrics dataframe
        self.basic_metric_statistics = {}
        self.algorithm_metric_statistics = {}
        self.metrics_statistics_df = pd.DataFrame()


    def generate_statistics_databases(self):
        
        # Get all unique data collections in the database
        self._set_datacollect_list()

        basic_metrics_dicts = {}
        algoritm_metrics_dicts = {}

        # Iterate through each data collection
        for data_collect_id in self.data_collect_list:
            # Get a dataframe for each data collection
            single_df = self._get_single_dataframe(data_collect_id)

            # Generate statistics for each data collection
            basic_dict = self._generate_basic_metrics(single_df, data_collect_id)
            algorithm_dict = self._generate_algorithm_metrics(single_df, data_collect_id)

            # Append statistics to overall statistics dictionary
            basic_metrics_dicts[data_collect_id] = basic_dict
            algoritm_metrics_dicts[data_collect_id] = algorithm_dict

        # Convert dictionaries to dataframes
        basic_df = self._convert_metrics_dict_to_dataframe(basic_metrics_dicts)
        algorithm_df = self._convert_metrics_dict_to_dataframe(algoritm_metrics_dicts)

        # Update stored dataframes with results of statistics calculations
        self.basic_movement_metrics_df = basic_df
        self.algorithm_movement_metrics_df = algorithm_df

        # Generate dataset summary statistics
        self.algorithm_metric_statistics = self._generate_metrics_statistics(algorithm_df)
        self.basic_metric_statistics = self._generate_metrics_statistics(basic_df)

        # Generate data frame of metric statistics
        self.metrics_statistics_df = self._convert_statistics_dicts_to_dataframe(
            [self.algorithm_metric_statistics, self.basic_metric_statistics], ["algorithm","basic"])

    def save_statistics_dfs(self):
        self._log_output("Saving basic metrics, algorithm metrics, and summary json")
        self.basic_movement_metrics_df.to_csv(self.basic_metrics_output_path)  
        self.algorithm_movement_metrics_df.to_csv(self.algorithm_metrics_output_path)  

        # Save metric statistics as JSON files to avoid recomputing for other applications
        with open(self.basic_metric_stats_output_path, "w") as outfile:
            json.dump(self.basic_metric_statistics, outfile, indent=4)
        
        with open(self.algorithm_metric_stats_output_path, "w") as outfile:
            json.dump(self.algorithm_metric_statistics, outfile, indent=4)

        # Save statistics as CSV for easier filtering
        self.metrics_statistics_df.to_csv(self.metric_stats_df_output_path)  

    def _convert_metrics_dict_to_dataframe(self, statistics_dict):
        # Method to convert metrics dictionaries to dataframes
        
        # Reformat dictionary into format ingestible by Pandas
        formatted_dict = {}
        for k, v in statistics_dict.items():
            for k2, v2 in v.items():
                if k2 in formatted_dict:
                    formatted_dict[k2].append(v2)
                else:
                    formatted_dict[k2] = [v2]

        # Convert dict to dataframe
        statistics_df = pd.DataFrame.from_dict(formatted_dict)

        return statistics_df
    
    def _convert_statistics_dicts_to_dataframe(self, statistics_dicts, metric_classes):
        # Method to convert statistics dictionaries to dataframes
        formatted_dict={}

        for i in range(len(statistics_dicts)):

            for k, v in statistics_dicts[i].items():
                # Initialize if no starting dictionary passed
                if "metric_name" in formatted_dict:
                    formatted_dict["metric_name"].append(k)
                else:
                    formatted_dict["metric_name"]=[k]

                if "metric_class" in formatted_dict:
                    formatted_dict["metric_class"].append(metric_classes[i])
                else:
                    formatted_dict["metric_class"]=[metric_classes[i]]

                # Port dictionary items to correct format
                for k2, v2 in v.items():
                    if k2 in formatted_dict:
                        formatted_dict[k2].append(v2)
                    else:
                        formatted_dict[k2] = [v2]

        # Convert dict to dataframe
        statistics_df = pd.DataFrame.from_dict(formatted_dict)

        return statistics_df

    def _generate_basic_metrics(self, single_df, data_collect_name):
        # Define empty dictionary for statistics
        single_stats_dict = {}
        single_stats_dict['data_collect_name'] = data_collect_name

        sensor_locations = ['head','left','right','bigball']
        motion_types = ['pos','rot']
        pos_axes = ['x','y','z']
        rot_axes = ['i','j','k','l']

        time_array = single_df['elapsed_time'].to_numpy()
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

                        # TODO - replace with dictionary or list of functions
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

    def _generate_algorithm_metrics(self, single_full_df, data_collect_name):
        # ,time,chapitre,leftballscount,rightballscount,

        # Separate data frame by chapter for analysis and create dataframe list to enable iteration
        # Hardcode chapter_list: # Dataset variation causes some issues if pulling from movement DF
        chapter_list = [1.0, 2.0, 3.0, 4.0] 
        df_dict = {}
        for chapter in chapter_list:
            df_dict[chapter]=single_full_df[single_full_df['chapitre']==chapter]

        # Establish dictionary to track metrics
        single_stats_dict = {}
        single_stats_dict['data_collect_name'] = data_collect_name

        # Set base metric names
        metric_planar_distance_traveled = "planar_distance_traveled_chapter-"
        metric_cartesian_distance_traveled = "cartesian_distance_traveled_chapter-"
        planar_distance_traveled_allchapters = 0 # Skips chapter 4, should be end of experience
        cartesian_distance_traveled_allchapters = 0 # Skips chapter 4, should be end of experience

        for chapter_num, chapter_df in df_dict.items():

            total_planar_dist_one_chap = 0
            total_cartesian_dist_one_chap = 0

            # Get numpy arrays of data to enable metrics
            x_array = chapter_df['head_pos_x'].to_numpy()
            y_array = chapter_df['head_pos_y'].to_numpy()
            z_array = chapter_df['head_pos_z'].to_numpy()

            # TODO - speed up by eliminating for loop
            for i in range(len(x_array)-1):
                total_planar_dist_one_chap += np.sqrt((x_array[i+1]-x_array[i])**2 + (z_array[i+1]-z_array[i])**2)
                total_cartesian_dist_one_chap += np.sqrt((x_array[i+1]-x_array[i])**2 + (y_array[i+1]-y_array[i])**2 + (z_array[i+1]-z_array[i])**2)

            single_stats_dict[f"{metric_planar_distance_traveled}{chapter_num}"] = total_planar_dist_one_chap

            if chapter_num<=3:
                planar_distance_traveled_allchapters+=total_planar_dist_one_chap
                cartesian_distance_traveled_allchapters+=total_cartesian_dist_one_chap

        single_stats_dict[f"{metric_planar_distance_traveled}all"] = planar_distance_traveled_allchapters
        single_stats_dict[f"{metric_cartesian_distance_traveled}all"] = cartesian_distance_traveled_allchapters

        # Balls collected metrics
        chapter = 1
        left_balls_collected = df_dict[chapter]["leftballscount"].to_numpy()
        right_balls_collected = df_dict[chapter]["rightballscount"].to_numpy()

        left_collect_max = left_balls_collected.max()
        right_collect_max = right_balls_collected.max()
        single_stats_dict["left_balls_collected_chapter-1"] = left_collect_max
        single_stats_dict["right_balls_collected_chapter-1"] = right_collect_max
        single_stats_dict["total_balls_collected_chapter-1"] = left_collect_max+right_collect_max

        # TODO - implement inertia measurement
        # Inertia - assumed fixed inertias of hands and head

        # TODO - implement angular momentum measurement
        # Angular Momentum - assumed fixed weights and intertias

        # TODO - implement clustering measurement for maze to assess stationary vs. exploration

        print(single_stats_dict.__len__())

        return single_stats_dict
    
    def _generate_metrics_statistics(self, dataset_metrics_df):
        self._log_output("Generating metrics statistics summaries")

        metrics_statistics_dict = {}

        for column in dataset_metrics_df.columns:
            if column == "data_collect_name":
                continue

            # Establish nested dictionary for each column
            column_dict = {}

            # Add metrics to column dict
            column_dict["mean"] = float(dataset_metrics_df[column].mean())
            column_dict["median"] = float(dataset_metrics_df[column].median())
            column_dict["skew"] = float(dataset_metrics_df[column].skew())
            column_dict["min"] = float(dataset_metrics_df[column].min())
            column_dict["max"] = float(dataset_metrics_df[column].max())
            column_dict["std_dev"] = float(dataset_metrics_df[column].std())
            column_dict["range"] = float(column_dict["max"]-column_dict["min"])

            # Assign column dict to metrics_statistics_dict
            metrics_statistics_dict[column]=column_dict

        return metrics_statistics_dict




    def _set_datacollect_list(self):
        self.data_collect_list = self.raw_movement_df['dataset_id'].unique()

    def _get_single_dataframe(self,data_collect_name):
        single_df = self.raw_movement_df.loc[self.raw_movement_df['dataset_id'] == data_collect_name]
        return single_df

    def _log_output(self, to_output):
        print(f"{__class__.__name__}: {to_output}") 

if __name__ == "__main__":
    cbmds = CollectiveBodyMovementDataStatistics(
        movement_database_path="data/movement_database/raw_movement_database.csv",
        statistics_output_path="data/movement_database/")
    cbmds.generate_statistics_databases()
    cbmds.save_statistics_dfs()