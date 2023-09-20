
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
        self.canvas_dataset_dict = {}
        self.total_canvas_height = height
        self.total_canvas_width = width

        self.canvas_indices = None

        # Set canvas frame sizes based on count
        self.canvas_frame_dimension = None
        self.title_span = None
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
        self.canvas_gallery_title.grid(row=0, column=0,columnspan=self.title_span, sticky=tk.N+tk.S+tk.E+tk.W)

        # Add canvas frames to grid
        for i in range(0, self.num_canvases):
            # Set canvas frame positions
            row_val = self.canvas_indices[i][0]+1
            col_val = self.canvas_indices[i][1]
            print(f"row {row_val}, col {col_val}")

            # Add canvas frame to grid
            self.canvas_dict[i].grid(row=row_val, column=col_val, sticky=tk.N+tk.S+tk.E+tk.W)

    def start_all(self,loaded_dataset, selected_metric):
        for num, canvas_frame in self.canvas_dict.items():
            canvas_frame.start(loaded_dataset, selected_metric)

    def stop_all(self):
        for num, canvas_frame in self.canvas_dict.items():
            canvas_frame.stop()
    
    def set_speed_all(self, speed):
        for num, canvas_frame in self.canvas_dict.items():
            canvas_frame.set_speed(speed)

    # TODO - implement dictionary method
    def get_frame_dataset_dict(self):
        pass

    # TOD0 - replace with dictionary method
    def load_datasets(self, loaded_dataset, selected_metric):
        for num, canvas_frame in self.canvas_dict.items():
            canvas_frame.load_frame_dataset(loaded_dataset, selected_metric)

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
            self.canvas_indices = [(0,0), (0,1), (0,2), (1,0), (1,1), (1,2)]

            # TODO - potnetial to split into height and width to account for toolbar space
            match self.num_canvases:
                case 1:
                    self.canvas_frame_dimension = min_dim
                    self.title_span = 1
                case 2:
                    if size_ratio >=2:
                        self.canvas_frame_dimension = min_dim
                    else:
                        self.canvas_frame_dimension = int(self.total_canvas_width / 2)
                    self.title_span = 2
                case 3:
                    if size_ratio >=3:
                        self.canvas_frame_dimension = min_dim
                    else:
                        self.canvas_frame_dimension = int(self.total_canvas_width / 3)
                    self.title_span = 3
                case _:
                    if size_ratio >=3:
                        self.canvas_frame_dimension = int(min_dim/2)
                    else:
                        self.canvas_frame_dimension =int(min(self.total_canvas_width / 3, min_dim/2))

                    self.title_span = 3



    def _log_output(self, to_output):
        print(f"{__class__.__name__}: {to_output}")

class ColletiveBodyMovementCanvasFrame(tk.Frame):

    def __init__(self,master, frame_num, height, width, canvas_dimenson=500) -> None:
        # Initiate the base frame
        tk.Frame.__init__(self, master, background="green")

        # Configure the window grid inherited from tk.Frame
        self._log_output(f"Configuring canvas frame {frame_num} ")
        self.canvas_dim = canvas_dimenson
        self.frame_num = frame_num

        # Initialize frame title text and other control inputs
        self.session_num = None
        self.actor_num = None
        self._create_text_variables()
        self._update_text_variables()

        self._configure_grid()

        # Initialize datasets and metrics for playback
        self.selected_dataset = None
        self.selected_metric = None
        self.visualization_index = 0
        

        # Create and pack widgets
        self.create_wigets()
        self.pack_widgets()

    def create_wigets(self):
        self._log_output(f"Creating widgets for canvas frame {self.frame_num}")

        # Create title
        self.canvas_title = tk.Label(self, textvariable=self.frame_title_text, justify=tk.CENTER)

        # Create canvas
        self.vis_canvas = tk.Canvas(self, height=self.canvas_dim, width=self.canvas_dim, background="white")

        # Create Session and headset options
        self.session_number_entry = tk.Entry(self, textvariable=self.session_number_var, width=3) #  background="white"
        self.headset_number_entry = tk.Entry(self, textvariable=self.headset_number_var, width=3)


    def update_canvas_frame_session(self, session_num):
        self.session_num = session_num
        self._update_text_variables()

    def update_canvas_frame_dat(self, actor_num):
        self.actor_num = actor_num
        self._update_text_variables()

    def load_frame_dataset(self, raw_movement_df, selected_metric):
        self.selected_metric = selected_metric
        session_num=self.session_number_var.get()
        headset_num=self.headset_number_var.get()

        # TODO - add checks for none / invalid datasets
        
        self._log_output(f"Loading session number {session_num} with headset number {headset_num}")

        self.loaded_dataset = raw_movement_df.loc[(raw_movement_df["session_number"] == int(session_num)) & (raw_movement_df["headset_number"] == int(headset_num))]
        self._log_output(f"Single dataset loaded with {len(self.loaded_dataset)} entries")

    def _create_text_variables(self):
        self.frame_title_text = tk.StringVar()
        self.session_number_var=tk.StringVar()
        self.headset_number_var=tk.StringVar()

    def _update_text_variables(self, session_value=None, actor_value=None):
        self.frame_title_text.set(f"Session: {self.session_num} / Actor: {self.actor_num}")
        self.session_number_var.set(session_value)
        self.headset_number_var.set(actor_value)


    def pack_widgets(self):
        self._log_output("Packing widgets")
        
        # Add title to grid
        self.canvas_title.grid(row=0, column=0,columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W)

        # Add canvas to grid
        self.vis_canvas.grid(row=1, column=0, columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W)

        # Add selection options to grid
        self.session_number_entry.grid(row=2, column=0, columnspan=1, sticky=tk.N+tk.S+tk.E+tk.W)
        self.headset_number_entry.grid(row=2, column=1, columnspan=1, sticky=tk.N+tk.S+tk.E+tk.W)


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

