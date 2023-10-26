
import tkinter as tk

class ColletiveBodyMovementMetricFrame(tk.Frame):

    def __init__(self,master, height, width) -> None:
        # Initiate the base frame
        tk.Frame.__init__(self, master, background="purple")

        # Configure the window grid inherited from tk.Frame
        self._configure_grid()
        
        # Create and pack widgets
        self.create_wigets()
        self.pack_widgets()

    def load_metric(self, metric_summary_statistics, selected_metric):
        self._log_output("Loading metrics - not yet implemented")

    def create_wigets(self):
        self._log_output("Creating widgets for GUI")

        # TODO - implement packing and unpacking arguments with **kwargs https://www.shecancode.io/blog/unpacking-function-arguments-in-python
        # Create first widget - a label with words
        self.metrics_title = tk.Label(self, text="Mmovement Metrics", justify=tk.CENTER)  

    def pack_widgets(self):
        self._log_output("Packing widgets")

        self.metrics_title.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)

    def _configure_grid(self):
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)

    def _log_output(self, to_output):
        print(f"{__class__.__name__}: {to_output}")