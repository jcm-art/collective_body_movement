
import pathlib



class CollectiveBodyAlgorithmVisualizer:

    def __init__(self, movement_database_path, visualization_output_directory) -> None:
        self._log_output("Initializing visualization generator.")
        
        # Initialize file paths
        self.movement_database_path = pathlib.Path(movement_database_path)
        self.movement_database_path = self.movement_database_path/"movement_statistics_database.csv"
        self.vis_output_dir_path = pathlib.Path(visualization_output_directory)

        # Make directory if not available
        self.vis_output_dir_path.mkdir(parents=True, exist_ok=True)  



    def _log_output(self, to_output):
        print(f"{__class__.__name__}: {to_output}")

if __name__=="__main__":

    cbav = CollectiveBodyAlgorithmVisualizer(
        movement_database_path="data/movement_database/",
        visualization_output_directory="data/analysis/visualizations/",
    )