#!/usr/bin/env python

import tkinter as tk

from collective_body_movement.user_interface.movement_canvas_frame import ColletiveBodyMovementCanvasFrame
from collective_body_movement.user_interface.movement_control_frame import ColletiveBodyMovementControlFrame
from collective_body_movement.user_interface.movement_metric_frame import ColletiveBodyMovementMetricFrame
from collective_body_movement.user_interface.movement_console_frame import ColletiveBodyMovementConsoleFrame

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

        # Initialize empty widget list
        self.widget_list = []

        # Create and pack widgets
        self.create_subframes()
        #self.create_wigets()
        self.pack_widgets()

    def create_subframes(self):
        # Establish common parameters for all subframes
        frame_padding = 2

        # TODO - convert to a helper function
        # Create canvas frame
        self.widget_list.append({
            "widget": ColletiveBodyMovementCanvasFrame(self, height=self.window_height*4/5, width=self.window_width/2),
            "metadata": {
                "sticky": tk.N+tk.S+tk.E+tk.W,
                "padx": frame_padding,
                "pady": frame_padding,
                "column": 0,
                "row": 0,
                "rowspan": 2,
            }
        })


        # Create control frame
        self.widget_list.append({
            "widget": ColletiveBodyMovementControlFrame(self, height=self.window_height*2/5, width=self.window_width/2),
            "metadata": {
                "sticky": tk.N+tk.S+tk.E+tk.W,
                "padx": frame_padding,
                "pady": frame_padding,
                "column": 1,
                "row": 0,
            }
        })

        # Create metric frame
        self.widget_list.append({
            "widget": ColletiveBodyMovementMetricFrame(self, height=self.window_height*2/5, width=self.window_width/2),
            "metadata": {
                "sticky": tk.N+tk.S+tk.E+tk.W,
                "padx": frame_padding,
                "pady": frame_padding,
                "column": 1,
                "row": 1,
            }
        })

        # Create console frame
        self.widget_list.append({
            "widget": ColletiveBodyMovementConsoleFrame(self, height=self.window_height*1/5, width=self.window_width),
            "metadata": {
                "sticky": tk.N+tk.S+tk.E+tk.W,
                "padx": frame_padding,
                "pady": frame_padding,
                "column": 0,
                "row": 2,
                "columnspan": 2,

            }
        })
        
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

        for item in self.widget_list:
            widget = item["widget"]
            print(item["metadata"])
            if type(item["metadata"]) is dict:
                print(item["metadata"])
                widget.grid(item["metadata"])
                widget.grid_propagate(0)
            else:
                # TODO - define default args for grid
                widget.grid()
        
    def start_gui(self):
        self._log_output("Starting GUI")
        # Start the event loop to wait for user input, clicks, redraw, etc
        self.mainloop() 


    def _configure_grid(self):
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)

        # Make the top level window expandable
        # TODO - look at expanding
        top=self.winfo_toplevel()
        top.geometry(f"{self.window_width}x{self.window_height}")
        top.minsize(self.window_width, self.window_height)
        top.maxsize(self.window_width, self.window_height)
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
    cbmag.start_gui()