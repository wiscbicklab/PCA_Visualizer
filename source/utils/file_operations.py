import os
import time
import chardet
import pandas as pd
from tkinter import filedialog, messagebox

OUTPUT_DIR = "output"  # Default directory for saving plots


def load_csv_file():
    """Load and validate CSV file."""
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    try:
        with open(file_path, 'rb') as file:
            result = chardet.detect(file.read())
        encoding = result['encoding']
        return pd.read_csv(file_path, encoding=encoding)
    except FileNotFoundError:
        pass
        

def save_plot(self, output_dir):
        """Preserve original save functionality."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        plot_filename = f'plot_{timestamp}.png'
        save_path = os.path.join(output_dir, plot_filename)
        try:
            self.fig.savefig(save_path)
            return save_path
        except Exception as e:
            raise Exception(f"Could not save the plot: {str(e)}")


