import pathlib
import sys
import argparse

from preprocessing.raw_movement_data_cleaning import CollectiveBodyDataCleaner
from analysis.raw_movement_data_plotting import CollectiveBodyRawMovementAnalysis
from analysis.generate_movement_data_statistics import CollectiveBodyMovementDataStatistics

class CollectiveBodyDataPipeline:

    def __init__(self,
                 raw_data_path,
                 raw_database_output_path) -> None:

        self.raw_data_path = pathlib.Path(raw_data_path)
        self.raw_database_output_path = pathlib.Path(raw_database_output_path)

    def run_pipeline(self, skip_ingest=False, quick_run=False):
        if skip_ingest==False:
            self.import_clean_data(quick_run)
        self.generate_statistics()
        self.generate_plots()

    def import_clean_data(self, quick_run):
        cbdc = CollectiveBodyDataCleaner(
            input_path=self.raw_data_path,
            output_path=self.raw_database_output_path
            )
        cbdc.import_data(fast_debug=quick_run, fast_debug_limit=10)
        cbdc.save_clean_data()

    def generate_statistics(self):
        cbmds = CollectiveBodyMovementDataStatistics(
            movement_database_path="data/movement_database/raw_movement_database.csv",
            statistics_output_path="data/movement_database/movement_statistics_database.csv"
        )
        cbmds.generate_statistics_database()
        cbmds.save_statistics_df()

    def generate_plots(self):
        cbma = CollectiveBodyRawMovementAnalysis(
            movement_database_path="data/movement_database/raw_movement_database.csv",
            plot_output_directory="data/analysis/")

        cbma.generate_scatter_plots()    
        cbma.generate_box_plots()
        cbma.generate_spot_plots()



if __name__=="__main__":
    # Get arguments from pipeline execution
    parser = argparse.ArgumentParser(
                    prog='Data Ingest and Analysis Pipeline',
                    description='This program runs the data ingest and analysis pipeline for the collective body movement project.',
                    epilog='Enjoy the program! :)')

    # Add arguments to pipeline execution
    parser.add_argument('--skip_raw_data_ingest',default=False) 
    parser.add_argument('--quick_run', default=False) 

    # Get arguments from command
    aaa = parser.parse_args()
    skip_ingest_arg = aaa.skip_raw_data_ingest
    quick_run = aaa.skip_raw_data_ingest

    # Initialize the pipeline
    cbdp = CollectiveBodyDataPipeline(
        raw_data_path="bin/data/DATA.2023.06.26/",
        raw_database_output_path="data/movement_database/",
    )

    # Run the pipeline with provided arguments
    cbdp.run_pipeline(skip_ingest=skip_ingest_arg, quick_run=quick_run)