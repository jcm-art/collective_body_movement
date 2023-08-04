import tkinter as tk


class ColletiveBodyMovementAnalysisGUI(tk.Frame):

    def __init__(self,master=None) -> None:
        # Initiate the base frame
        tk.Frame.__init__(self, master)

        # Configure the window grid inherited from tk.Frame
        self.grid()

        # Set application title 
        self.master.title('Sample application')

        # Initialize empty widget list
        self.widget_list = []

        # Create and pack widgets
        self.create_wigets()
        self.pack_widgets()

    def create_wigets(self):
        self._log_output("Creating widgets")


        # Create first widget - a label with words
        widget_item = {}
        w = tk.Label(self.root, text="Hello, world!")  

        widget_item["widget"] = w
        widget_item["metadata"] = "TBD"

        self.widget_list.append(widget_item)

        # Create second widget
        widget_item = {}
        myButton = tk.Button(self.root, text="Exit", command=self._buttonPushed)
        widget_item["widget"] = myButton
        widget_item["metadata"] = "TBD"

        self.widget_list.append(widget_item)


    def pack_widgets(self):
        self._log_output("Packing widgets")

        for item in self.widget_list:
            widget = item["widget"]
            widget.grid()

    def start_gui(self):
        self._log_output("Starting GUI")
        # Start the event loop to wait for user input, clicks, redraw, etc
        self.mainloop() 

    def _buttonPushed(self): 
        self._log_output("Exiting the application")
        self.root.destroy()

    def _log_output(self, to_output):
        print(f"{__class__.__name__}: {to_output}")

if __name__ == "__main__":
    cbmag = ColletiveBodyMovementAnalysisGUI()
    cbmag.start_gui()