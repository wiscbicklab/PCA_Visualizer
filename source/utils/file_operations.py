import os
import time
import chardet
import pandas as pd

OUTPUT_DIR = "output"  # Default directory for saving plots


def load_file(file_path):
    """Load and validate CSV file."""
    with open(file_path, 'rb') as file:
        result = chardet.detect(file.read())
    encoding = result['encoding']
    return pd.read_csv(file_path, encoding=encoding)


def save_plot(fig, filename_prefix="plot", output_dir=OUTPUT_DIR):
    """Save plot with timestamp to a specified directory."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    plot_filename = f'{filename_prefix}_{timestamp}.png'
    save_path = os.path.join(output_dir, plot_filename)
    fig.savefig(save_path)
    return save_path
