
import tkinter as tk
import pandas as pd

class ColletiveBodyMovementControlFrame(tk.Frame):

    def __init__(self, master, height, width) -> None:
        # Initiate the base frame
        tk.Frame.__init__(self, master, background="blue", height=height, width=width)

        self.frame_width = width
        self.frame_height = height

        # Configure the window grid inherited from tk.Frame
        self._configure_grid()

        # Create StringVars for control input
        self._create_control_inputs()

        # Create and pack widgets
        self._create_wigets()

        self._set_default_text()

        self._add_widgets_to_grid()

    def _create_control_inputs(self):
        self.database_location=tk.StringVar()
        self.session_number_var=tk.StringVar()
        self.headset_number_var=tk.StringVar()
        self.metric_var = tk.StringVar()


    def _create_wigets(self):
        self._log_output("Creating widgets for GUI")

        # Create title for frame
        self.control_title = tk.Label(self, text="Control Panel", justify=tk.CENTER)

        # Load database widgets
        self.load_database_button = tk.Button(self, text="Load Database / Metrics", command=self._load_database)
        self.database_path_entry = tk.Entry(self, textvariable=self.database_location) #  background="white"

        # Load dataset widgets
        self.load_dataset_button = tk.Button(self, text="Load Dataset", command=self._load_dataset)
        self.session_num_label = tk.Label(self, text="Session Number: ", justify=tk.RIGHT)
        self.session_number_entry = tk.Entry(self, textvariable=self.session_number_var) #  background="white"
        self.headset_num_label = tk.Label(self, text="Headset Number: ", justify=tk.RIGHT)
        self.headset_number_entry = tk.Entry(self, textvariable=self.headset_number_var)

        # Metrics
        self.load_metric_button = tk.Button(self, text="Select Metric", command=self._select_metric)
        # TODO - replace with option menu https://stackoverflow.com/questions/15884075/tkinter-in-a-virtualenv
        self.select_metric_entry = tk.Entry(self, textvariable=self.metric_var)

        # Start / Stop / Play
        self.start_canvas_button = tk.Button(self, text="Start", command=self._start_canvas)
        self.stop_canvas_button = tk.Button(self, text="Stop", command=self._stop_canvas)
        self.export_canvas_button = tk.Button(self, text="Export Vis", command=self._export_canvas)



    def _set_default_text(self):
        self.database_location.set("data/movement_database/")
        self.session_number_var.set("1")
        self.headset_number_var.set("1")
        self.metric_var.set("left_balls_collected_chapter-1")
        

    def _add_widgets_to_grid(self):
        self._log_output("Packing widgets")

        # Add title to frame
        self.control_title.grid(row=0, column=0, columnspan=3, sticky=tk.N+tk.S+tk.E+tk.W)

        # Add database load to frame
        self.load_database_button.grid(row=1, column=0, columnspan=1, sticky=tk.N+tk.S+tk.E+tk.W)
        self.database_path_entry.grid(row=1, column=1, columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W)

        # Add dataset selection to frame
        self.load_dataset_button.grid(row=2, column=0, rowspan=2, sticky=tk.N+tk.S+tk.E+tk.W)
        self.session_num_label.grid(row=2, column=1, columnspan=1, sticky=tk.N+tk.S+tk.E+tk.W)
        self.session_number_entry.grid(row=2, column=2, columnspan=1, sticky=tk.N+tk.S+tk.E+tk.W)
        self.headset_num_label.grid(row=3, column=1, columnspan=1, sticky=tk.N+tk.S+tk.E+tk.W)
        self.headset_number_entry.grid(row=3, column=2, columnspan=1, sticky=tk.N+tk.S+tk.E+tk.W)

        # Add metrics selection to frame
        self.load_metric_button.grid(row=4, column=0, columnspan=1, sticky=tk.N+tk.S+tk.E+tk.W)
        self.select_metric_entry.grid(row=4, column=1, columnspan=2, sticky=tk.N+tk.S+tk.E+tk.W)

        # Add canvas controls to frame
        self.start_canvas_button.grid(row=5, column=0, columnspan=1, sticky=tk.N+tk.S+tk.E+tk.W)
        self.stop_canvas_button.grid(row=5, column=1, columnspan=1, sticky=tk.N+tk.S+tk.E+tk.W)
        self.export_canvas_button.grid(row=5, column=2, columnspan=1, sticky=tk.N+tk.S+tk.E+tk.W)


    def _configure_grid(self):
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)

    def _load_database(self):
        database_path=self.database_location.get()
        self._log_output(f"Loading database at path {database_path}")
        
        # TODO - offload functionality to another class
        self.raw_movement_df = pd.read_csv(database_path + "raw_movement_database.csv")
        self._log_output(f"Database load completed with {len(self.raw_movement_df)} entries")


    def _load_dataset(self):
        session_num=self.session_number_var.get()
        headset_num=self.headset_number_var.get()
        
        self._log_output(f"Loading session number {session_num} with headset number {headset_num}")

        self.loaded_dataset = self.raw_movement_df.loc[(self.raw_movement_df["session_number"] == int(session_num)) & (self.raw_movement_df["headset_number"] == int(headset_num))]
        self._log_output(f"Single dataset loaded with {len(self.loaded_dataset)} entries")

    def _select_metric(self):
        pass

    def _start_canvas(self):
        pass

    def _stop_canvas(self):
        pass

    def _export_canvas(self):
        pass

    def _log_output(self, to_output):
        print(f"{__class__.__name__}: {to_output}")