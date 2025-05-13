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
        print("No file selected")
        return None

    try:
        with open(file_path, 'rb') as file:
            result = chardet.detect(file.read())
        encoding = result['encoding']
        return pd.read_csv(file_path, encoding=encoding)
    except FileNotFoundError:
        print("File not found.")
        

def save_plot(fig, filename_prefix="plot", output_dir=OUTPUT_DIR):
    """Save plot with timestamp to a specified directory."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    plot_filename = f'{filename_prefix}_{timestamp}.png'
    save_path = os.path.join(output_dir, plot_filename)
    fig.savefig(save_path)
    return save_path


