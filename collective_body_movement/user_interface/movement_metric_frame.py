
import tkinter as tk

class ColletiveBodyMovementMetricFrame(tk.Frame):

    def __init__(self,master, height, width) -> None:
        # Initiate the base frame
        tk.Frame.__init__(self, master, background="purple", height=height, width=width)

        # Configure the window grid inherited from tk.Frame
        self._configure_grid()

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

    def pack_widgets(self):
        self._log_output("Packing widgets")

        for item in self.widget_list:
            widget = item["widget"]
            if type(item["metadata"]) is dict:
                widget.grid(item["metadata"])
            else:
                # TODO - define default args for grid
                widget.grid()

    def _configure_grid(self):
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)

    def _log_output(self, to_output):
        print(f"{__class__.__name__}: {to_output}")