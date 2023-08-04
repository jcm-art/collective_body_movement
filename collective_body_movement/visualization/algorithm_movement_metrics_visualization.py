
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle
import pathlib


class CollectiveBodyAlgorithmVisualizer:

    def __init__(self, movement_database_path, visualization_output_directory, num_visualizations=1) -> None:
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

'''
# Load data for analysis

raw_movement_df = pd.read_csv(cleaned_data_output_path + 'raw_movement_database.csv')
movement_summary_df = pd.read_csv(cleaned_data_output_path + 'raw_movement_summary_database.csv')
movement_statistics_df = pd.read_csv(statistics_database_output_path + 'movement_statistics_database.csv')

def distance_traveled_metric_score(distance_traveled, mean_dist, std_dist):
  cut_off_std = 3 # Should cover 99.9% of the population

  # Get standard deviations from mean for distance traveled
  score_std = (distance_traveled - mean_dist) / std_dist

  # Clip scores to min/max range
  if score_std < -1*cut_off_std:
    score_std = -1*cut_off_std
  elif score_std > cut_off_std:
    score_std = cut_off_std


  normalized_score = (score_std+cut_off_std)/(cut_off_std*2)

  return normalized_score


def select_a_dataset(movement_df, session_id, headset_id):
  single_dataset = raw_movement_df.loc[movement_df['session_number'] == session_id]
  single_dataset = single_dataset.loc[movement_df['headset_number'] == headset_id]
  return single_dataset

def visualize_a_dataset(data_frame,metric_bounds, down_sample_factor = 10, live_display = True):

  x_head = np.array(data_frame['head_pos_x'])
  z_head = np.array(data_frame['head_pos_z'])

  cummulative_dist = [0]
  cummulative_dist_score = [0]
  for i in range(1,len(x_head)):
    new_dist = ((x_head[i]-x_head[i-1])**2 + (x_head[i]-x_head[i-1])**2 )**0.5
    cummulative_dist.append(cummulative_dist[i-1]+new_dist)
    cummulative_dist_score.append(distance_traveled_metric_score(cummulative_dist[i],metric_bounds[0],metric_bounds[1]))

  # Create figure for animation

  # Define Limits of Plot
  fig = plt.figure()

  ax = plt.axes(xlim=(-3,10),ylim=(-2,2))
  ax.set_title("Collective Body - Participant Movement")
  ax.set_xlabel("X axis travel")
  ax.set_ylabel("Z axis travel")

  # Hide X and Y axes label marks
  ax.xaxis.set_tick_params(labelbottom=False)
  ax.yaxis.set_tick_params(labelleft=False)

  # Hide X and Y axes tick marks
  ax.set_xticks([])
  ax.set_yticks([])

  my_distance = 0.0

  scat = ax.scatter(x_head[0], z_head[0], c='b', s=5)
  path_been = ax.plot(x_head[0],z_head[0], c='r',lw=0.5,ls='-')[0]
  extra_dist = Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0)
  extra_score = Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0)
  my_legend = ax.legend([scat, path_been, extra_dist, extra_score],['head_position',
                                                  'head_path',
                                                  "Distance Traveled: {:.2f}".format(cummulative_dist[0]),
                                                  "Distance Score: {:.2f}".format(cummulative_dist_score[0])])

  def init():
    x = x_head[0]
    z = z_head[0]


    data = np.stack([x,z]).T
    scat.set_offsets(data)

    path_been.set_xdata(x_head[0])
    path_been.set_ydata(z_head[0])

    my_legend.get_texts()[2].set_text("Distance Traveled: {:.2f}".format(cummulative_dist[0]))
    my_legend.get_texts()[3].set_text("Distance Score: {:.2f}".format(cummulative_dist_score[0]))


    return (scat, path_been, my_legend)

  def update(frame):
    x = x_head[frame*down_sample_factor]
    z = z_head[frame*down_sample_factor]
    my_distance = cummulative_dist[frame*down_sample_factor]
    my_distance_score = cummulative_dist_score[frame*down_sample_factor]

    data = np.stack([x,z]).T
    scat.set_offsets(data)

    path_been.set_xdata(x_head[:frame*down_sample_factor])
    path_been.set_ydata(z_head[:frame*down_sample_factor])


    # Update Legend
    my_legend.get_texts()[2].set_text("Distance Traveled: {:.2f}".format(my_distance))
    my_legend.get_texts()[3].set_text("Distance Score: {:.2f}".format(my_distance_score))

    return (scat, path_been, my_legend, my_distance)

  anim = FuncAnimation(fig=fig, func=update, init_func=init, frames = int(len(x_head)/down_sample_factor), interval = 50)

  # Showing videos is broken
  #plt.close(anim._fig)
  #fig.show()
  #HTML(anim.to_html5_video())

  if down_sample_factor >= 25:
    anim.save('data_animation.gif', writer = 'imagemagick', fps=20)

  anim.save('data_animation.mp4', writer = 'ffmpeg', fps=20)



my_dataset = select_a_dataset(raw_movement_df, 1, 1)

# TOD0 - Generate XZ distance
mean_metric = movement_statistics_df['total_distance_traveled'].mean()
std_metric = movement_statistics_df['total_distance_traveled'].std()

visualize_a_dataset(my_dataset, [mean_metric, std_metric], down_sample_factor=1,)
'''