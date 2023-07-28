
import pathlib
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import colorsys



class CollectiveBodyMovementStatisticsAnalysis:

    def __init__(self, movement_database_path, plot_output_directory) -> None:
        self.movement_statistics_database = pathlib.Path(movement_database_path)
        self.plot_output_directory = pathlib.Path(plot_output_directory)

        # Import Database
        self.movement_statistics_df = pd.read_csv(self.movement_statistics_database, index_col=0)

    def generate_scatter_plots(self):
        print("Movement statistics scatter plots not yet implemented")
        pass

    def generate_spot_plots(self, num_plots=10):
        print("Movement statistics spot plots not yet implemented")
        pass

    def generate_box_plots(self):
        print("Movement statistics box plots not yet implemented")
        pass


    def generate_histogram_plots(self):
        numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
        numeric_df = self.movement_statistics_df.select_dtypes(include=numerics)

        for col in numeric_df.columns:
            print(f"Generating histogram for {col}")
            fig, axs = plt.subplots(figsize=(12, 4))
            numeric_df[col].plot.hist(bins=30, alpha=0.5, ax=axs)

            axs.set_title(f"Histogram for participants {col}")
            axs.set_xlabel(f"Bins for {col}")
            axs.set_ylabel("Counts")

            fig.savefig(self.plot_output_directory/f"{col}_scatter_plot.png")         
            # plt.show() 
            plt.close(fig) 


    def _get_rgb_tuples(self, n_colors):
        # Generate plot colors
        HSV_tuples = [(x*1.0/n_colors, 0.5, 0.5) for x in range(n_colors)]
        RGB_tuples = list(map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples))
        return RGB_tuples

if __name__=="__main__":
    print("Analyzing data from collective body raw movement data.")

    cbma = CollectiveBodyMovementStatisticsAnalysis(
        movement_database_path="data/movement_database/movement_statistics_database.csv",
        plot_output_directory="data/analysis/movement_statistics/")
    
    cbma.generate_scatter_plots()    
    cbma.generate_box_plots()

    cbma.generate_spot_plots()