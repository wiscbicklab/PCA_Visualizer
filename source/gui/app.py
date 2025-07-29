import platform
import tkinter as tk
from tkinter import VERTICAL, Scrollbar, filedialog, messagebox

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Core functionality imports
from source.analysis.pca import PCAAnalyzer
from source.utils.constant import *

# Components Imports
from source.gui.clean_data_box import CleanDataBox
from source.gui.setting_box import SettingBox
from source.gui.create_plot_box import CreatePlotBox
from source.gui.app_state  import AppState
import source.utils.file_operations as file_ops


class PCAAnalysisApp(tk.Tk):
    """GUI Application for PCA Analysis."""

    #### 0. Setup GUI Elements ####

    def __init__(self):
        """
        Initialize the GUI_Application
        """
        # Sets up the window, and creates a way to track the app state
        super().__init__()
        self.app_state = AppState(self)
        
        self.title("PCA Analysis Tool")
        self.configure(bg="#f5f5f5")

        # Object for running PCA analysis
        self.pca_analyzer = PCAAnalyzer()

        # Declare scrollable section
        self.options_scroll = None
        self.options_canvas = None
        self.options_window = None
        self.options_frame = None

        # Declare the custom component
        self.pca_box = None
        self.plot_box = None
        self.settings_box = None

        # Declare space for the figure to be stored
        self.plot_canvas = None
        self.plot_canvas_figure = None

        # Results Section
        self.program_status_lbl = None
        self.program_status_text = None
        self.data_text = None
        self.pca_text = None

        # Save Button
        self.save_data_bttn = None
        self.save_plot_bttn = None

        # Set up the application
        self.create_components()
        self.setup_layout()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_components(self):
        """Creates the components to be placed onto this tk Frame"""
        # Creates canvas and figure where plots will be displayed
        self.plot_canvas = FigureCanvasTkAgg(self.app_state.fig, master=self)
        self.plot_canvas_figure = self.plot_canvas.get_tk_widget()

        # Creates a scrollable window 
        self.options_canvas = tk.Canvas(self, width=450)
        self.options_scroll = Scrollbar(self, orient=VERTICAL, command=self.options_canvas.yview)
        self.options_canvas.configure(yscrollcommand=self.options_scroll.set)
        self.options_frame = tk.Frame(self.options_canvas, **BG_COLOR)
        self.options_window = self.options_canvas.create_window(
            (0, 0),
            window=self.options_frame,
            anchor="nw",
            tags="options_frame"
        )
        self.options_canvas.bind(
            "<Configure>",
            lambda e: [
                self.options_canvas.configure(scrollregion=self.options_canvas.bbox("all")),
                self.options_canvas.itemconfig("options_frame", width=e.width)
            ]
        )
        # Bind mouse wheel scrolling (cross-platform)
        self.options_canvas.bind("<Enter>", lambda e: self._bind_mousewheel())
        self.options_canvas.bind("<Leave>", lambda e: self._unbind_mousewheel())

        # Output Directory Section
        self.output_dir_label = tk.Label(
            self,
            text=f"Output Directory: {self.app_state.output_dir}",
            **LABEL_STYLE,
            wraplength=300,  # Wrap text for long paths
            anchor="w", justify="left")
        self.output_dir_button = tk.Button(
            self,
            text="Select Output Directory",
            **BUTTON_STYLE,
            command=self.select_output_directory
        )

        # Intialize Custom components
        self.pca_box = CleanDataBox(self.options_frame, self.app_state, **BG_COLOR)
        self.plot_box = CreatePlotBox(self.options_frame, self.app_state, **BG_COLOR)
        self.settings_box = SettingBox(self.options_frame, self.app_state, **BG_COLOR)



        # Text Information Boxes
        self.program_status_lbl = tk.Label(self, text="Program Status:", **LABEL_STYLE)
        self.program_status_text = tk.Text(self, height=1, width=48, **LABEL_STYLE)
        self.program_status_text.insert(tk.END, "Please Load Data!")
        self.data_text = tk.Text(self, height=15, width=75, **LABEL_STYLE)
        self.data_text.insert(tk.END, "Information will appear here once data has been loaded!")
        self.pca_text = tk.Text(self, height=15, width=80, **LABEL_STYLE)
        self.pca_text.insert(tk.END, "Information will appear once PCA has been run!")

        # Save buttons
        self.save_data_bttn = tk.Button(
            self,
            text="Save Data",
            **BUTTON_STYLE,
            command=lambda: file_ops.save_data_csv(self.app_state.df, self.app_state.output_dir)
        )
        self.save_plot_bttn = tk.Button(
            self,
            text="Save Plot",
            **BUTTON_STYLE,
            command=lambda: file_ops.save_plot(self.app_state.fig, self.app_state.output_dir)
        )

    def setup_layout(self):
        """Setup the layout of GUI components"""
        # Configure grid weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=0)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_columnconfigure(4, weight=1)
        self.grid_columnconfigure(5, weight=1)

        # Adds plot and scrollable
        self.options_canvas.grid(row=0, column=0, rowspan=5, padx=10, pady=10, sticky="nswe")
        self.options_scroll.grid(row=0, column=1, rowspan=5, sticky="nsew")
        self.plot_canvas_figure.grid(row=0, column=2, rowspan=3, columnspan=4, padx=10, pady=10, sticky="nw")
        
        # Sets up custom Components
        self.pca_box.grid(row=2, column=0, padx=10, pady=10, sticky="we")
        self.plot_box.grid(row=3, column=0, padx=10, pady=10, sticky="we")
        self.settings_box.grid(row=4, column=0, padx=10, pady=10, sticky="we")
        
        # Results Section
        self.program_status_lbl.grid(row=3, column=2, padx=5, pady=5, sticky='se')
        self.program_status_text.grid(row=3, column=3, padx=5, pady=5, sticky='sw')
        self.data_text.grid(row=4, column=2, columnspan=2, padx=5, pady=5, sticky="nsw")
        self.pca_text.grid(row=4, column=4, columnspan=2, padx=5, pady=5, sticky="nsew")

        # Save Buttons
        self.save_data_bttn.grid(row=5, column=2, padx=5, pady=5, sticky="w")
        self.save_plot_bttn.grid(row=5, column=3, padx=5, pady=5, sticky="e")

        # Output Directory
        self.output_dir_label.grid(row=5, column=4, padx=5, pady=5, sticky="e")
        self.output_dir_button.grid(row=5, column=5, padx=5, pady=5, sticky="e")


    #### 1. DATA HANDLING METHODS ####

    def run_analysis(self):
        """Execute PCA analysis."""
        # Skip analysis if data isn't cleaned or if data has not changed
        if not self.app_state.df_cleaned.get() or not self.app_state.df_updated.get():
            # Update display
            text = self.create_pca_text(self.app_state.pca_results)
            self.replace_pca_text(text)

        try:
            # Run analysis and store the result
            self.app_state.pca_results = self.pca_analyzer.analyze(
                df=self.app_state.df,
                n_components=self.app_state.num_pca_comp.get(),
            )

            # Update display
            text = self.create_pca_text(self.app_state.pca_results)
            self.replace_pca_text(text)

            # Update df status variables
            self.app_state.df_updated.set(False)

        except ValueError as e:
            print(e.with_traceback)
            messagebox.showerror("Analysis Error", str(ve))
        except Exception as e:
            print(e.with_traceback)
            messagebox.showerror("Error", f"PCA analysis failed: {str(e)}")

    def select_output_directory(self):
        """Allow the user to select an output directory for saving plots."""
        selected_dir = filedialog.askdirectory()
        if selected_dir:  # If the user selects a directory
            self.app_state.output_dir = selected_dir
            self.output_dir_label.config(text=f"Output Directory: {self.app_state.output_dir}")
            messagebox.showinfo("Directory Selected", f"Output directory set to:\n{self.app_state.output_dir}")
        else:
            messagebox.showerror("No Directory Selected", f"Output directory set to:\n{self.app_state.output_dir}.")
      
    
    #### 4. UI UPDATE METHODS ####

    def replace_status_text(self, text):
        """Replaces the text in the program status text widget"""
        self.program_status_text.delete(1.0, tk.END)
        self.program_status_text.insert(tk.END, text)

        self.update_figure()

    def replace_data_text(self, text):
        """Replaces the text in the data text widget"""
        # Insert the info_text into the GUI widget
        self.data_text.delete(1.0, tk.END)
        self.data_text.insert(tk.END, text)

        self.update_figure()

    def replace_pca_text(self, text):
        """Replaces the text in the pca text widget"""
        self.pca_text.delete(1.0, tk.END)
        self.pca_text.insert(tk.END, text)

        self.update_figure()
    

    def update_figure(self):
        # Destroy old canvas
        self.app_state.main.plot_canvas_figure.destroy()
        # Adjusts Layout to avoid cutoff
        self.app_state.fig.tight_layout()

        # Create new canvas with updated figure
        self.app_state.main.plot_canvas = FigureCanvasTkAgg(self.app_state.fig, master=self.app_state.main)
        self.app_state.main.plot_canvas.draw()

        # Get the Tkinter widget and add it to the grid
        self.app_state.main.plot_canvas_figure = self.app_state.main.plot_canvas.get_tk_widget()
        self.app_state.main.plot_canvas_figure.grid(row=0, column=2, rowspan=3, columnspan=4, padx=10, pady=10, sticky="nw")

    def create_blank_fig(self, grid=True, subplot_shape=111):
        self.app_state.fig = Figure(self.app_state.fig_size)
        self.app_state.ax = self.app_state.fig.add_subplot(subplot_shape)
        self.app_state.ax.grid(grid)


    #### 5. EVENT HANDLERS ####

    def on_close(self):
        if self.plot_canvas:
            self.plot_canvas.get_tk_widget().destroy()
        plt.close('all')
        self.destroy()

    def _bind_mousewheel(self):
        # Windows and macOS
        self.options_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        # Linux
        self.options_canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.options_canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self):
        self.options_canvas.unbind_all("<MouseWheel>")
        self.options_canvas.unbind_all("<Button-4>")
        self.options_canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        if event.num == 4:  # Linux scroll up
            self.options_canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Linux scroll down
            self.options_canvas.yview_scroll(1, "units")
        else:  # Windows/macOS
            self.options_canvas.yview_scroll(-1 * (event.delta // 120), "units")


    #### Text Generation ####
    def create_pca_text(self, pca_results):
        # Simple, clean formatting
        text = "PCA Analysis Results\n"
        text += "══════════════════\n\n"

        # Basic Information
        text += f"Number of components: {pca_results['n_components']}\n"
        text += f"Original shape: {pca_results['original_shape']}\n"
        text += f"Prepared shape: {pca_results['prepared_shape']}\n\n"

        # Explained Variance Section
        text_cols = [f"PC{i + 1}: {var:.3f}" for i, var in enumerate(pca_results['explained_variance'])]
        text += self.format_col_text(text_cols, "Explained Variance Ratios:\t", sep=",\t")

        return text
    
    def format_col_text(self, cols, start_text="", line_limit=80, sep=", "):
        if cols is None or len(cols) == 0:
            return start_text + "None\n"
        
        lines = []
        current_line = start_text
        for col in cols:
            item_str = (sep if current_line != start_text else "") + col
            if len(current_line) + len(item_str) > line_limit:
                lines.append(current_line)
                current_line = col
            else:
                current_line += item_str
        if current_line:
            lines.append(current_line)
        
        return "\n".join(lines) + "\n"





TASKBAR_TOPBAR_HEIGHT = 125 #CHANGES OFFSET LEFT TO AVOID TASKBAR OVERLAP


# Start App
if __name__ == "__main__":   
        app = PCAAnalysisApp()

        os_type = platform.system()

        if os_type == "Windows" or os_type == "Darwin":
            app.state("zoomed")
        else: 
            # Get screen dimensions
            screen_width = app.winfo_screenwidth()
            screen_height = app.winfo_screenheight()-TASKBAR_TOPBAR_HEIGHT

            # Set the window geometry to the full screen size
            app.geometry(f"{screen_width}x{screen_height}+0+0")


        # Prevent window Resizing
        app.resizable(False, False)
        app.title("PCA Visualizer")

        app.mainloop()


