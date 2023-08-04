import pathlib
import sys
import argparse

from preprocessing.raw_movement_data_cleaning import CollectiveBodyDataCleaner
from analysis.generate_movement_data_statistics import CollectiveBodyMovementDataStatistics
from visualization.raw_movement_data_plotting import CollectiveBodyRawMovementPlots
from visualization.basic_movement_metrics_plotting import CollectiveBodyMovementBasicMetricsPlots

class CollectiveBodyDataPipeline:

    def __init__(self,
                 raw_data_path,
                 raw_database_output_path,
                 statistics_database_output_path,
                 plot_output_directory) -> None:

        # Set paths
        self.raw_data_path = pathlib.Path(raw_data_path)
        self.raw_database_output_path = pathlib.Path(raw_database_output_path)
        self.statistics_database_outputh_path = pathlib.Path(statistics_database_output_path)
        self.plot_output_directory = pathlib.Path(plot_output_directory)

        # Make directories if they don't exist
        self.raw_database_output_path.mkdir(parents=True, exist_ok=True)
        self.statistics_database_outputh_path.mkdir(parents=True, exist_ok=True)
        self.plot_output_directory.mkdir(parents=True, exist_ok=True)

    def run_pipeline(self, skip_ingest, quick_run, skip_plots, skip_raw_plots, skip_basic_plots):
        print(f"Skip ingest parameter is {skip_ingest}")
        if skip_ingest:
            self._log_output("Skipping data ingest")
        else:
            self.import_clean_data(quick_run=quick_run)
        self.generate_statistics()
        
        if skip_plots:
            self._log_output("Skipping plot generation")
        else:
            self.generate_plots(skip_raw_plots, skip_basic_plots)

    def import_clean_data(self, quick_run):
        self._log_output("Importing and cleaning data")
        cbdc = CollectiveBodyDataCleaner(
            input_path=self.raw_data_path,
            output_path=self.raw_database_output_path
        )
        cbdc.import_data(fast_debug=quick_run, fast_debug_limit=10)
        cbdc.save_clean_data()

    def generate_statistics(self):
        self._log_output("Generating statistics")
        # TODO make names static constants
        cbmds = CollectiveBodyMovementDataStatistics(
            movement_database_path=self.raw_database_output_path,
            statistics_output_path= self.statistics_database_outputh_path
        )
        cbmds.generate_statistics_databases()
        cbmds.save_statistics_dfs()

    def generate_plots(self, skip_raw_plots, skip_basic_plots):
        self._log_output("Generating visualizations")

        # Skip plots of raw statistics if enabled
        if skip_raw_plots==False:
            cbma = CollectiveBodyRawMovementPlots(
                movement_database_path=self.raw_database_output_path,
                plot_output_directory=self.plot_output_directory/"raw_movement_plots/",
            )

            # Generate plots for raw movement data
            cbma.generate_scatter_plots()    
            cbma.generate_box_plots()
            cbma.generate_spot_plots()

        if skip_basic_plots==False:
            cbmsa = CollectiveBodyMovementBasicMetricsPlots(
                movement_database_path=self.statistics_database_outputh_path,
                plot_output_directory=self.plot_output_directory/"movement_statistics_plots/")

            # Generate histogram plots for all basic metrics
            cbmsa.generate_histogram_plots()    

    def _log_output(self, output):
        print(f"{__class__.__name__}: {output}")


if __name__=="__main__":
    # Get arguments from pipeline execution
    parser = argparse.ArgumentParser(
                    prog='Data Ingest and Analysis Pipeline',
                    description='This program runs the data ingest and analysis pipeline for the collective body movement project.',
                    epilog='Enjoy the program! :)')

    # Add arguments to pipeline execution
    parser.add_argument('--skip_raw_data_ingest',action='store_true', default=False) 
    parser.add_argument('--quick_run',action='store_true', default=False) 
    parser.add_argument('--skip_plots',action='store_true', default=False) 
    parser.add_argument('--skip_raw_plots',action='store_true', default=False) 
    parser.add_argument('--skip_basic_plots',action='store_true', default=False) 

    # Get arguments from command
    aaa = parser.parse_args()
    skip_ingest_arg = aaa.skip_raw_data_ingest
    quick_run = aaa.quick_run
    skip_plots = aaa.skip_plots
    skip_raw_plots = aaa.skip_raw_plots
    skip_basic_plots = aaa.skip_basic_plots

    # Initialize the pipeline
    # TODO - create options to specify path or use default locations specified in config file
    cbdp = CollectiveBodyDataPipeline(
        raw_data_path="bin/data/DATA.2023.06.26/",
        raw_database_output_path="data/movement_database/",
        statistics_database_output_path="data/movement_database/",
        plot_output_directory="data/analysis/"
    )

    # Run the pipeline with provided arguments
    print(f"Running pipline with skip_ingest={skip_ingest_arg}, quick_run={quick_run}, skip_plots={skip_plots}, skip_raw_plots={skip_raw_plots}, and skip_basic_plots={skip_basic_plots}")
    cbdp.run_pipeline(skip_ingest=skip_ingest_arg, 
                      quick_run=quick_run, 
                      skip_plots=skip_plots, 
                      skip_raw_plots=skip_raw_plots, 
                      skip_basic_plots=skip_basic_plots)