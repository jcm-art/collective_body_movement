
import tkinter as tk

class ColletiveBodyMovementCanvasFrame(tk.Frame):

    def __init__(self,master, height, width) -> None:
        # Initiate the base frame
        tk.Frame.__init__(self, master, background="green")

        # Configure the window grid inherited from tk.Frame
        self._configure_grid()

        # Create and pack widgets
        self.create_wigets()
        self.pack_widgets()

    def create_wigets(self):
        self._log_output("Creating widgets for GUI")

        # Create title
        self.canvas_title = tk.Label(self, text="Movement Visualization", justify=tk.CENTER)

        # Create canvas
        self.vis_canvas = tk.Canvas(self, height=500, width=500, background="white")

    def pack_widgets(self):
        self._log_output("Packing widgets")
        
        # Add title to grid
        self.canvas_title.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)

        # Add canvas to grid
        self.vis_canvas.grid(row=1, column=0, sticky=tk.N+tk.S+tk.E+tk.W)


    def start(self, selected_dataset, selected_metric):
        self._log_output("Starting canvas - not yet implemented")

        # TODO - update loop after start
        #      root.after(1000, mainLoop) #Calls mainLoop every 1 second.
        # https://stackoverflow.com/questions/12892180/how-to-get-the-name-of-the-master-frame-in-tkinter
        # https://stackoverflow.com/questions/62543178/in-python-is-there-a-way-to-set-a-tkinter-update-timer-that-is-non-blocking-wh


    def stop(self):
        self._log_output("Stopping canvas - not yet implemented")

    def _configure_grid(self):
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)

    def _log_output(self, to_output):
        print(f"{__class__.__name__}: {to_output}")