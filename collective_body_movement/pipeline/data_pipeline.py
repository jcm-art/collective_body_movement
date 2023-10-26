# Collective Body Movement Application
# Director: Sarah Silverblatt-Buser (https://www.sarahsilverblatt.com/)
# Author: Justin Martin (jcm-art)

import argparse
import pathlib
from typing import Dict, List

import pandas as pd

from collective_body_movement.ingest.directory_ingest import DirectoryParserBolt
from collective_body_movement.preprocessing.cleaner import DataCleanerBolt
from collective_body_movement.preprocessing.kinematics import KinematicsBolt
from collective_body_movement.preprocessing.metrics import MetricsBolt
from collective_body_movement.postprocessing.aggregation import AggregatorBolt
from collective_body_movement.postprocessing.reports import ReportBolt
from collective_body_movement.utils import CollectiveBodyBolt

class CollectiveBodyDataPipeline:

    def __init__(self, final_output_path: str) -> None:

        # Set paths
        self.final_output_directory = pathlib.Path(final_output_path)

        # TODO - make saving intermediate steps optional
        self._initialize_filesystem()

        # Initialize Preprocessing Flow 
        # TODO - add configuration, manage with pipeline instead of manual stages
        self.directory_parser = DirectoryParserBolt(self.input_file_info, save_intermediate_output=True)
        self.data_cleaner = DataCleanerBolt(self.monolithic_database_path, save_intermediate_output=True)
        self.kinematics_generator = KinematicsBolt(self.temporary_kinematics_path, save_intermediate_output=True)
        self.metrics_generator = MetricsBolt(self.algorithm_metrics_path, save_intermediate_output=True)
        self.aggregator_bolt = AggregatorBolt(self.final_output_path, save_intermediate_output=True)
        self.report_bolt = ReportBolt(self.report_path, save_intermediate_output=True)
        
        self._pipeline: List[CollectiveBodyBolt] = [
            self.directory_parser, self.data_cleaner, self.kinematics_generator, 
            self.metrics_generator, self.aggregator_bolt, self.report_bolt
        ]


    def initialize_input(self, raw_data_path, file_ingest_limit: int = None, quick_debug: bool = False):
        # TODO - enable starting from different inputs, not just raw file system data
        # TODO - enable batching of data

        # Initialize datastructures for bolt processing pipeline
        # TODO - reimplement as class or struct
        self.initial_df_list: List[pd.DataFrame] = []
        self.initial_aggregate_metadata = {
            "input_metadata": {
                "directory_root_path": raw_data_path,
                "quick_debug_mode": quick_debug,
                "file_ingest_limit": file_ingest_limit,
            }
        }
        self.initial_metadata_list: List[Dict] = []

        return self.initial_df_list, self.initial_aggregate_metadata, self.initial_metadata_list

    def run_pipeline(self):
        
        # TODO - investigate updating with jump table to remove excessive logic
        # TODO - enable skipping pipeline steps
        # TODO - move pipeline to batch based argument with pre-step for 
        # getting file paths and batches

        output_df_list, output_aggregate_metadata, output_metadata_list = \
            self.initial_df_list, self.initial_aggregate_metadata, self.initial_metadata_list

        # Data ingest and cleaning stage
        for pipeline_stage in self._pipeline:
            output_df_list, output_aggregate_metadata, output_metadata_list = \
                pipeline_stage.process(output_df_list, output_aggregate_metadata, output_metadata_list)

        # Return df and metadata
        return output_df_list, output_aggregate_metadata, output_metadata_list

    def _initialize_filesystem(self):
        # Define directory structure
        self.input_file_info = self.final_output_directory / "input_info/"
        self.monolithic_database_path = self.final_output_directory / "monolithic_database/"
        self.temporary_kinematics_path = self.final_output_directory / "tmp_kinematics_database/"
        self.algorithm_metrics_path = self.final_output_directory / "algorithm_database/"
        self.final_output_path = self.final_output_directory / "final_output/"
        self.report_path = self.final_output_directory / "reports/"

        # Make directories if they don't exist
        self.final_output_path.mkdir(parents=True, exist_ok=True)
        self.monolithic_database_path.mkdir(parents=True, exist_ok=True)
        self.temporary_kinematics_path.mkdir(parents=True, exist_ok=True)
        self.algorithm_metrics_path.mkdir(parents=True, exist_ok=True)
        self.final_output_path.mkdir(parents=True, exist_ok=True)
        self.report_path.mkdir(parents=True, exist_ok=True)

    def _log_output(self, output):
        print(f"{__class__.__name__}: {output}")


if __name__=="__main__":
    # Get arguments from pipeline execution
    parser = argparse.ArgumentParser(
                    prog='Data Ingest and Analysis Pipeline',
                    description='This program runs the data ingest and analysis pipeline for the collective body movement project.',
                    epilog='Enjoy the program! :)')

    # Add arguments to pipeline execution
    # TODO - redo arguments
    parser.add_argument('--skip_raw_data_ingest',action='store_true', default=False) 
    parser.add_argument('--quick_run',action='store_true', default=False) 

    # Get arguments from command
    # TODO - redo arguments
    aaa = parser.parse_args()
    skip_ingest_arg = aaa.skip_raw_data_ingest
    quick_run = aaa.quick_run

    # Initialize the pipeline
    # TODO - create options to specify path or use default locations specified in config file
    cbdp = CollectiveBodyDataPipeline(
        final_output_path="data/new_pipeline/",
    )

    # Run the pipeline with provided arguments
    # TODO - easier print function for arguments
    raw_data_path="bin/data/DATA.2023.06.26/"
    cbdp._log_output(f"Running pipeline with {raw_data_path}")

    input_df_list, input_aggregated_metadata, output_metadata = \
        cbdp.initialize_input(raw_data_path=raw_data_path, file_ingest_limit=10, quick_debug=True)
    output_df_list, output_aggregated_metadata, output_metadata_list = \
          cbdp.run_pipeline()

    # Temporary for debug
    #print("Final dataframe is: ")
    #print(output_df.describe())    
    print("Final output metadata is:")
    print(output_aggregated_metadata)