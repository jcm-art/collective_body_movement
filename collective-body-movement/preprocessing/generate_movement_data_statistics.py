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
            statistics_df = self._generate_statistics(single_df)

            # Append statistics to overall statistics dataframe
            self.movement_statistics_df = pd.concat([self.movement_statistics_df, statistics_df], ignore_index=True)

    def save_statistics_df(self):
        self._log_output("Saving raw database and skipped file information")
        self.sta.parent.mkdir(parents=True, exist_ok=True)  
        self.movementdf.to_csv(self.output_path)  


    def _generate_statistics(self, single_df):
        pass

    def _get_datacollect_list(self):
        self.data_collect_list = self.raw_movement_df['data_collection_example'].unique()

    def _get_single_dataframe(self,data_collect_name):
        pass

if __name__ == "__main__":
    cbmds = CollectiveBodyMovementDataStatistics(
        movement_database_path="data/movement_database/raw_movement_database.csv",
        statistics_output_path="data/movement_database/movement_statistics_database.csv")
    cbmds.generate_statistics_database()