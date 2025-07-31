import os
import time
import webbrowser
import chardet
import pandas as pd
from tkinter import filedialog, messagebox

import plotly

def load_csv_file():
    """Load and validate CSV file."""
    # Asks user to select a csv file
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])

    # Ensures the user selected an appropriate file
    if not file_path:
        return None
    if not file_path.lower().endswith(".csv"):
        messagebox.showerror("File Error", f"You selected: {file_path}\nYou must select a .csv file instead!")
        return None

    # Attempts to load user data file
    try:
        with open(file_path, 'rb') as file:
            result = chardet.detect(file.read())
        encoding = result['encoding']
        df = pd.read_csv(file_path, encoding=encoding)
        if df.empty:
            messagebox.showerror("Loadings Error", "File was opened, but no data was found!")
            return None
        else:
            return df
    except OSError as e:
        print(e.strerror)
        messagebox.showerror("File Error", f"An error occurred while opening the file: {e}")
        return None
        
def save_plot(fig, output_dir):
        """
        Saves a figure as a png image
        
        Finds or creates the ouput_dir and save the figure there using a time stamped name.
            Shows an error message if the file could not be saved.
        
        Args:
            fig: Is the biplot figure to be saved and opened
            output_dir: Is the path where the file will be saved

        Returns:
            The save_path including file_name of the saved figure. None if an error occurred
        """
        # Creates the output path if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Creates a file_name and save_path
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        plot_filename = f'plot_{timestamp}.png'
        save_path = os.path.join(output_dir, plot_filename)

        # Saves the figure to the save_path
        try:
            fig.savefig(save_path)
        except Exception as e:
            messagebox.showerror(
                "File Error",
                f"An error occured attempting to save the figure.\t{e}"
            )
            return None
        messagebox.showinfo("Plot Saved", f"Plot Sucsessfully Saved at {save_path}")
        return save_path

def save_interactive_plot(fig, output_dir):
    """
    Save an interactive biplot figure as an html file and opens it in the users browser

    Args:
        fig: Is the biplot figure to be saved and opened
        output_dir: Is the path where the file will be saved
    
    Returns:
        The save_path including file_name of the saved figure. None if an error occurred
    """
    # Creates the output path if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create file_name and save_path
    time_stamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"Interactive_Biplot_{time_stamp}.html"
    save_path = os.path.join(output_dir, filename)


    config = {
        'scrollZoom': True,
        'displayModeBar': True,
        'editable': True
    }
    try:
        # Save the figure to the file save path
        plotly.io.write_html(fig, file=save_path, config=config)

        # Open the file in the users webrowser
        webbrowser.open(f'file://{os.path.abspath(save_path)}')
    except Exception as e:
        messagebox.showerror("File Error", f"An error occured attempting to save and open the interactive biplot.\t{e}")
        return None

    messagebox.showinfo("Plot Saved", f"Plot Sucsessfully Saved at {save_path}")
    return save_path

def save_data_csv(df: pd.DataFrame, output_dir):
    """
    Saves a pandas dataframe as a csv and shows a message regaurding the save status
    
    Args:
        df: A pd.DataFrame to be saved to a file
        output_dir: The directory where the data file should be stored

    Returns:
        The full path to where the file is saved or None if the file doesn't save properly
    """
    # Creates the output path if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create file_name and save_path
    time_stamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"Program_Data_{time_stamp}.csv"
    save_path = os.path.join(output_dir, filename)


    try:
        df.to_csv(save_path, index=False)
    except Exception as e:
        messagebox.showerror("Save Error", "An error occured while attempting to save the current program data")
        return None
    
    messagebox.showinfo("Data Saved", f"The current program data has been saved to {save_path}")
    return save_path
    





