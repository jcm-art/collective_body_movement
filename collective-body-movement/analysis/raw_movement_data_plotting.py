
import pathlib
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import colorsys



class CollectiveBodyRawMovementAnalysis:

    def __init__(self, movement_database_path, plot_output_directory) -> None:
        self.movement_database = pathlib.Path(movement_database_path)
        self.plot_output_directory = pathlib.Path(plot_output_directory)

        # Import Database
        self.movementdf = pd.read_csv(self.movement_database, index_col=0)

    def generate_scatter_plots(self):
        print("Plotting graphs")

        client_list = self.movementdf['client_number'].unique()
        num_clients = len(client_list)

        RGB_tuples = self._get_rgb_tuples(num_clients)

        print(client_list)
        fig, axs = plt.subplots(figsize=(12, 4))

        for i in range(num_clients):
            client_data = self.movementdf.loc[self.movementdf['client_number'] == client_list[i]]
            client_data.plot(x="timestamp_from_start", y="headpos_x", kind='scatter', color=RGB_tuples[i],s=1,ax=axs)                   
        
        axs.set_xlabel("Time (ns)")          
        axs.set_ylabel("Head Position X (cm)")    
        axs.legend(client_list)      
        fig.savefig(self.plot_output_directory/"scatter_plot.png")         
        # plt.show() 
        plt.close(fig) 

    def generate_spot_plots(self, num_plots=10):
        print("Generating spot plots")
        column_list = ["headpos_x", "headpos_y", "headpos_z"]
        collection_list = self.movementdf['data_collection_example'].unique()

        # Get colors
        RGB_tuples = self._get_rgb_tuples(len(column_list))

        # Make output directory for plots
        random_output = self.plot_output_directory/"random_plots"
        random_output.mkdir(parents=True, exist_ok=True)  

        counter = 0
        while counter < num_plots:

            random_collection_num = np.random.randint(0, len(collection_list))

            fig, axs = plt.subplots(figsize=(12, 4))

            client_data = self.movementdf.loc[self.movementdf['data_collection_example'] == collection_list[random_collection_num]]

            color_num = 0
            for column in column_list:
                client_data.plot(x="timestamp_from_start", y=column, kind='scatter', color=RGB_tuples[color_num], ax=axs)   
                color_num += 1                
            
            axs.set_xlabel("Time (s)")          
            axs.set_ylabel("Head Position X/Y/Z (m)")    
            axs.legend(column_list)      
            fig.savefig(random_output/f"plot{counter}.png")         
            # plt.show() 
            plt.close(fig) 

            counter+=1

    def generate_box_plots(self):
        print("Creating box plots")

        fig, axs = plt.subplots(figsize=(12, 4))

        self.movementdf.boxplot(column='headpos_x',by='client_number', ax=axs)                   
        
        axs.set_xlabel("Client")          
        axs.set_ylabel("Head Position X (cm)")          
        fig.savefig(self.plot_output_directory/"box_plot.png")         
        # plt.show() 
        plt.close(fig) 

    def _get_rgb_tuples(self, n_colors):
        # Generate plot colors
        HSV_tuples = [(x*1.0/n_colors, 0.5, 0.5) for x in range(n_colors)]
        RGB_tuples = list(map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples))
        return RGB_tuples

if __name__=="__main__":
    print("Analyzing data from collective body raw movement data.")

    cbma = CollectiveBodyRawMovementAnalysis(
        movement_database_path="data/movement_database/raw_movement_database.csv",
        plot_output_directory="data/analysis/")
    
    cbma.generate_scatter_plots()    
    cbma.generate_box_plots()

    cbma.generate_spot_plots()