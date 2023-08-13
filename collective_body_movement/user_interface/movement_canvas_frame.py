
import tkinter as tk
import numpy as np


class ColletiveBodyMovementCanvasGallery(tk.Frame):
        
    def __init__(self,master, height=810, width=1620, num_canvases=1) -> None:
        # Initiate the base frame
        tk.Frame.__init__(self, master, background="teal")

        # Define the starting number of canvases
        if num_canvases <=6 or num_canvases < 1 :
            self.num_canvases = num_canvases
        else:
            raise Exception("Number of canvases must be between 1 and 6")
        self.canvas_dict = {}
        self.total_canvas_height = height
        self.total_canvas_width = width

        self.canvas_indices = None

        # Set canvas frame sizes based on count
        self.canvas_frame_dimension = None
        self._update_canvas_frame_size()

        # Create and pack widgets
        self.create_wigets()
        self.pack_widgets()

    def create_wigets(self):
        self._log_output("Creating CanvasFrames for CanvasGallery")

        
        for i in range(0,self.num_canvases):
            # Create canvas frame
            self.canvas_dict[i] = ColletiveBodyMovementCanvasFrame(self, frame_num=i, height=self.canvas_frame_dimension, width=self.canvas_frame_dimension, canvas_dimenson=self.canvas_frame_dimension)
            
        # Create title
        self.canvas_gallery_title = tk.Label(self, text="Movement Visualizations", justify=tk.CENTER)

    def pack_widgets(self):
        self._log_output("Packing widgets")
        
        # Add title to grid
        self.canvas_gallery_title.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)

        # Add canvas frames to grid
        for i in range(0, self.num_canvases):
            # Set canvas frame positions
            row_val = self.canvas_indices[i][0]+1
            col_val = self.canvas_indices[i][1]
            print(f"row {row_val}, col {col_val}")

            # Add canvas frame to grid
            self.canvas_dict[i].grid(row=row_val, column=col_val, sticky=tk.N+tk.S+tk.E+tk.W)


    def _update_canvas_frame_size(self):
        # Get smallest dimension of total frame
        min_dim = np.min([self.total_canvas_height, self.total_canvas_width])
        max_dim = np.max([self.total_canvas_height, self.total_canvas_width])
        size_ratio = int(np.floor(max_dim/min_dim))

        # TODO - implement automatic resizing for horizontal and vertical
        self.landscape_gallery = True 

        # Allocate dimensions based on number of canvases
        if self.landscape_gallery:
            # Set indices of canvases
            self.canvas_indices = [(0,0), (0,1), (0,2), (0,1), (1,1), (2,1)]

            # TODO - potnetial to split into height and width to account for toolbar space
            match self.num_canvases:
                case 1:
                    self.canvas_frame_height = min_dim
                    self.canvas_frame_width = min_dim
                case 2:
                    if size_ratio >=2:
                        self.canvas_frame_dimension = min_dim
                    else:
                        self.canvas_frame_dimension = int(self.total_canvas_width / 2)
                case 3:
                    if size_ratio >=3:
                        self.canvas_frame_dimension = min_dim
                    else:
                        self.canvas_frame_dimension = int(self.total_canvas_width / 3)



        

    def _log_output(self, to_output):
        print(f"{__class__.__name__}: {to_output}")

class ColletiveBodyMovementCanvasFrame(tk.Frame):

    def __init__(self,master, frame_num, height, width, canvas_dimenson=500) -> None:
        # Initiate the base frame
        tk.Frame.__init__(self, master, background="green")

        # Configure the window grid inherited from tk.Frame
        self.canvas_dim = canvas_dimenson
        print("Frame ")
        self._configure_grid()

        # Initialize datasets and metrics for playback
        self.selected_dataset = None
        self.selected_metric = None
        self.visualization_index = 0

        # Create and pack widgets
        self.create_wigets()
        self.pack_widgets()

    def create_wigets(self):
        self._log_output("Creating widgets for GUI")

        # Create title
        self.canvas_title = tk.Label(self, text="Movement Visualization", justify=tk.CENTER)

        # Create canvas
        self.vis_canvas = tk.Canvas(self, height=self.canvas_dim, width=self.canvas_dim, background="white")

    def pack_widgets(self):
        self._log_output("Packing widgets")
        
        # Add title to grid
        self.canvas_title.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)

        # Add canvas to grid
        self.vis_canvas.grid(row=1, column=0, sticky=tk.N+tk.S+tk.E+tk.W)


    def start(self, selected_dataset, selected_metric):
        self._log_output("Starting Movement Visualization")

        # TODO - check if dataset changed and reconfigure if so
        self.is_running = True
        self.speed = 1
        if self.visualization_index == 0:
            self.selected_dataset = selected_dataset
            self.selected_metric = selected_metric
            self._configure_movement_visualization()
        else:
            self._animate_participant()


    def _configure_movement_visualization(self):
        # Get overall dataset bounds for visualization to translate coordiante frames
        # TODO - remove hardcoded x and z values
        self.global_head_pos_x_max = 3
        self.global_head_pos_x_min = -3
        self.global_head_pos_z_max = 3
        self.global_head_pos_z_min = -3

        # Get position data to start visualization
        self.head_pos_x = self.selected_dataset["head_pos_x"].to_numpy()
        self.head_pos_z = self.selected_dataset["head_pos_z"].to_numpy()
        self.chapters = self.selected_dataset["chapitre"].to_numpy()
        self.animation_length = len(self.head_pos_x )

        # Set size of head
        self.head_size = 3

        self.x = int((self.global_head_pos_x_max-self.head_pos_x[self.visualization_index])/(self.global_head_pos_x_max-self.global_head_pos_x_min)*self.canvas_dim)
        self.z = int((self.global_head_pos_z_max-self.head_pos_z[self.visualization_index])/(self.global_head_pos_z_max-self.global_head_pos_z_min)*self.canvas_dim)

        coord = [self.x, self.z, self.x+5, self.z+5]

        self.circle = self.vis_canvas.create_oval(coord, outline="blue", fill="blue")

        self.window = self.master.master
        self._animate_participant()

    def _animate_participant(self):
        # Function to animate the Collective Body Movement participant
        self.visualization_index+=self.speed

        self.x_next = int((self.global_head_pos_x_max-self.head_pos_x[self.visualization_index])/(self.global_head_pos_x_max-self.global_head_pos_x_min)*self.canvas_dim)
        self.z_next = int((self.global_head_pos_z_max-self.head_pos_z[self.visualization_index])/(self.global_head_pos_z_max-self.global_head_pos_z_min)*self.canvas_dim)

        x_vel = self.x_next - self.x
        z_vel = self.z_next - self.z

        # Draw prior path
        color = "gray"
        if self.chapters[self.visualization_index] == 1:
            color = "red"
        elif self.chapters[self.visualization_index] == 2:
            color = "blue"
        elif self.chapters[self.visualization_index] == 3:
            color = "green"

        self.vis_canvas.create_line(self.x,self.z,self.x_next,self.z_next, fill=color, width=1)

        # TODO - put circle on top
        self.vis_canvas.move(self.circle, x_vel, z_vel)


        coordinates = self.vis_canvas.coords(self.circle)
        self.x = coordinates[0]
        self.z = coordinates[1]
        if self.visualization_index < self.animation_length-self.speed:
            if self.is_running:
                self.window.after(33, self._animate_participant)
        else:
            self.visualization_index = 0
            self.is_running = False

    def stop(self):
        self._log_output("Stopping canvas - not yet implemented")
        self.is_running = False

    def set_speed(self, speed):
        self.speed = speed

    def _configure_grid(self):
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)

    def _log_output(self, to_output):
        print(f"{__class__.__name__}: {to_output}")

