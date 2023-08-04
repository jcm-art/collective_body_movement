#!/usr/bin/env python

import tkinter as tk


class ColletiveBodyMovementAnalysisGUI(tk.Frame):

    def __init__(self,master=None) -> None:
        # Initiate the base frame
        tk.Frame.__init__(self, master)

        # Configure the window grid inherited from tk.Frame
        self._configure_grid()

        # Set application title 
        self.master.title('Collective Body Movement')

        # Initialize empty widget list
        self.widget_list = []

        # Create and pack widgets
        self.create_wigets()
        self.pack_widgets()

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
            if type(item["metadata"]) is dict:
                widget.grid(item["metadata"])
            else:
                # TODO - define default args for grid
                widget.grid()
        
    def start_gui(self):
        self._log_output("Starting GUI")
        # Start the event loop to wait for user input, clicks, redraw, etc
        self.mainloop() 


    def _configure_grid(self):
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)

        # Make the grid expandable
        top=self.winfo_toplevel()
        top.rowconfigure(0, weight=1, minsize=400)
        top.columnconfigure(0, weight=1,minsize=400)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)


    def _buttonPushed(self): 
        self._log_output("Button pushed!")

    def _log_output(self, to_output):
        print(f"{__class__.__name__}: {to_output}")

if __name__ == "__main__":
    cbmag = ColletiveBodyMovementAnalysisGUI()
    cbmag.start_gui()