#!/usr/bin/env python

import tkinter as tk

from collective_body_movement.user_interface.movement_canvas_frame import ColletiveBodyMovementCanvasFrame
from collective_body_movement.user_interface.movement_control_frame import ColletiveBodyMovementControlFrame
from collective_body_movement.user_interface.movement_metric_frame import ColletiveBodyMovementMetricFrame
from collective_body_movement.user_interface.movement_console_frame import ColletiveBodyMovementConsoleFrame


class CollectiveBodyGuiPlaybackManager:
    def __init__(self, gui):
        self.gui = gui

        # TODO - remove list and eliminate hard coding
        self.gui.control_frame.start_canvas_button.configure(command=self.start_button_callback)
        self.gui.control_frame.stop_canvas_button.configure(command=self.stop_button_callback)
        self.gui.control_frame.speed_1x_button.configure(command=self.speed_1x_button_callback)
        self.gui.control_frame.speed_5x_button.configure(command=self.speed_5x_button_callback)
        self.gui.control_frame.speed_10x_button.configure(command=self.speed_10x_button_callback)

    def start_button_callback(self):
        print("Play button pressed")
        # TODO - do not restart if already in progress
        loaded_dataset = self.gui.control_frame.get_loaded_dataset()
        metric_summary_statistics = self.gui.control_frame.get_metric_summary_statistics()
        selected_metric = self.gui.control_frame.get_chosen_metric()
        self.gui.canvas_frame.start(loaded_dataset, selected_metric)
        self.gui.metric_frame.load_metric(metric_summary_statistics, selected_metric)
    
    def stop_button_callback(self):
        print("Stop button pressed")
        self.gui.canvas_frame.stop()

    def speed_1x_button_callback(self):
        self.gui.canvas_frame.set_speed(1)
    
    def speed_5x_button_callback(self):
        self.gui.canvas_frame.set_speed(5)

    def speed_10x_button_callback(self):
        self.gui.canvas_frame.set_speed(10)


class ColletiveBodyMovementAnalysisGUI(tk.Frame):

    def __init__(self,master=None) -> None:
        # Initiate the base frame
        tk.Frame.__init__(self, master)

        self.window_width = 900
        self.window_height = 600

        # Configure the window grid inherited from tk.Frame
        self._configure_grid()

        # Set application title 
        self.master.title('Collective Body Movement')

        # Create and pack widgets
        self.create_subframes()
        self.pack_widgets()

    def create_subframes(self):
        # Establish common parameters for all subframes
        frame_padding = 2

        # Create canvas frame
        self.canvas_frame = ColletiveBodyMovementCanvasFrame(self, height=self.window_height*4/5, width=self.window_width/2)

        # Create control frame
        self.control_frame = ColletiveBodyMovementControlFrame(self, height=self.window_height*2/5, width=self.window_width/2)

        # Create metric frame
        self.metric_frame = ColletiveBodyMovementMetricFrame(self, height=self.window_height*2/5, width=self.window_width/2)

        # Create console frame
        self.console_frame = ColletiveBodyMovementConsoleFrame(self, height=self.window_height*1/5, width=self.window_width)
        
    def create_wigets(self):
        self._log_output("Creating widgets for GUI")

        # TODO - implement packing and unpacking arguments with **kwargs https://www.shecancode.io/blog/unpacking-function-arguments-in-python

        # Create first widget - a label with words
        widget_item = {}
        w = tk.Label(self, text="Hello, world!")  


        widget_item["widget"] = w
        widget_item["metadata"] = {
            "sticky": tk.N+tk.S+tk.E+tk.W,
        }

        self.widget_list.append(widget_item)

        # Create second widget
        widget_item = {}
        myButton = tk.Button(self, text="Push the button", command=self._buttonPushed)
        widget_item["widget"] = myButton
        widget_item["metadata"] = "TBD"
        self.widget_list.append(widget_item)

        # Create Exit button widget
        widget_item = {}
        myButton = tk.Button(self, text="Exit", command=self.quit)
        widget_item["widget"] = myButton
        widget_item["metadata"] = "TBD"
        self.widget_list.append(widget_item)

    def pack_widgets(self):
        self._log_output("Packing widgets")
        frame_padding = 2

        self.canvas_frame.grid(row=0, column=0, rowspan=2, padx=frame_padding, pady=frame_padding, sticky=tk.N+tk.S+tk.E+tk.W)
        self.control_frame.grid(row=0, column=1, padx=frame_padding, pady=frame_padding, sticky=tk.N+tk.S+tk.E+tk.W)
        self.metric_frame.grid(row=1, column=1, padx=frame_padding, pady=frame_padding, sticky=tk.N+tk.S+tk.E+tk.W)
        self.console_frame.grid(row=2, column=0, rowspan=2, padx=frame_padding, pady=frame_padding, sticky=tk.N+tk.S+tk.E+tk.W)
        
    def start_gui(self):
        self._log_output("Starting GUI")
        # Start the event loop to wait for user input, clicks, redraw, etc
        self.mainloop() 


    def _configure_grid(self):
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)

        # Make the top level window expandable
        # TODO - look at expanding
        #top=self.winfo_toplevel()
        #top.geometry(f"{self.window_width}x{self.window_height}")
        #top.minsize(self.window_width, self.window_height)
        #top.maxsize(self.window_width, self.window_height)
        '''top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)

        # Make the canvas expandable
        self.rowconfigure(0, weight=2)
        self.rowconfigure(1, weight=2)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)'''



    def _buttonPushed(self): 
        self._log_output("Button pushed!")

    def _log_output(self, to_output):
        print(f"{__class__.__name__}: {to_output}")

if __name__ == "__main__":
    cbmag = ColletiveBodyMovementAnalysisGUI()
    guimanager = CollectiveBodyGuiPlaybackManager(cbmag)
    cbmag.start_gui()