import pandas as pd
import pathlib

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

        # Iterate through each data collection
        for data_collect_name in self.data_collect_list:
            # Get a dataframe for each data collection
            single_df = self._get_single_dataframe(data_collect_name)

            # Generate statistics for each data collection
            statistics_df = self._generate_statistics(single_df,data_collect_name)

            # Append statistics to overall statistics dataframe
            self.movement_statistics_df = pd.concat([self.movement_statistics_df, statistics_df], ignore_index=True)

    def save_statistics_df(self):
        self._log_output("Saving raw database and skipped file information")
        print(self.movement_statistics_df)
        self.statistics_output_path.parent.mkdir(parents=True, exist_ok=True)  
        self.movement_statistics_df.to_csv(self.statistics_output_path)  


    def _generate_statistics(self, single_df, data_collect_name):
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

        single_stats_df = pd.DataFrame([data_collect_name], columns=['data_collect_name'])

        sensor_location = 'head'
        motion_type = 'pos'
        axes = 'x'
        derived_val = 'mean'
        new_column = sensor_location + '_' + motion_type + '_' + axes + '_' + derived_val

        statistic = single_df[sensor_location + '_' + motion_type + '_' + axes].mean()

        single_stats_df[new_column] = statistic

        return single_stats_df

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