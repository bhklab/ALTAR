import os
import time
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget
import pyqtgraph as pg


'''
A python script which provides a command line interface to
label the RadCure data as having dental artifacts or notself.

This implementation uses the H4H data transfer node.
TODO: Try writing something that can be run remotely.

This script saves one matplotlib figure to the home directory
for each patient (one at a time).

Instructions to run the app:
1. Login to H4H on the data transfer node (your_username@h4huhndata1)
This cannot be done remotely.
2. Start an interactive Slurm session with plenty of time and memory:
$ salloc -t 5:00:00 --mem 5G
3. Run this script with the command $ python config/script.py
4. Ensure xterm is installed on your local machine. From another terminal
login to the data transfer node with the -X option e.g.
$ ssh -X -p 22 username@172.27.23.173      # Data transfer node (UHN network)
$ ssh -X -p 10022 username@172.27.23.163   # Login node (UHN network)
$ ssh -X -p 5500 carrowsm@192.75.165.28    # Login node (remote)

matplotlib figures should appear on your local machine as you use the app.
'''


class LabelImageApp():
    """Command line interface to label images in a dataset."""
    def __init__(self):
        super(LabelImageApp, self).__init__()

        self.img_path = "/cluster/projects/bhklab/RADCURE/img/"           # Path to image directory (edit this here)
        self.csv_path = "/cluster/home/carrowsm/logs/artifact_labels.csv" # File containing the labels of the images
        self.log_path = "/cluster/home/carrowsm/logs/label/"               # Path to matplotlib files

        # Check this path exists
        self.verify_path()

        # Create the dataframe containing the labels
        self.label_df, self.index = self.init_label_df()

        # Initiate the pyqtgraph plot
        self.app = pg.image()



    # --- Initialization functions --- #
    def verify_path(self) :
        ''' See if the path to the data is valid'''
        if not os.access(self.img_path, os.F_OK) :
            raise ValueError("The directory {} cannot be found.".format(self.img_path))
            exit()

    def init_label_df(self) :
        """ Dataframe which will store the label for each patient. If a csv with
            this data exists, load it as a pandas dataframe. Otherwise, make one.
            Also    Load the most recent state of the labeling process.
                    Find the current patient ID (this is the first NaN if the
                    CSV is not being created for the first time).
        """
        # Load DF if there is a CSV
        if os.access(self.csv_path, os.F_OK) :
            df = pd.read_csv(self.csv_path, dtype=str, na_values=['nan', 'NaN'])
            df["has_artifact"] = df["has_artifact"].astype(int)

            # Find the first artifact status which is NaN (last_valid_index gives last non-NaN)
            current_patient = df["has_artifact"].last_valid_index() + 1

        else :
            # Get all the patient IDs
            ids = []
            for file in os.listdir(self.img_path) :
                ids.append(file.split("_")[0])   # Get the ID from the filename

            # Create a dataframe indexed integers
            df = pd.DataFrame(data={"patient_id": ids, "has_artifact": np.nan})
            current_patient = 0                 # Set the current patient index to 0
        return df, current_patient


    # --- Interface helper functions --- #
    def clear_image(self, file_name) :
        # Remove the image from the logging directory
        try :
            log = os.path.join(self.log_path, file_name)   # Where img was stored for plotting
            os.remove(log)
        except FileNotFoundError :
            return

    def send_image(self, file_name) :
        src = os.path.join(self.img_path, file_name)   # Where to copy img from
        log = os.path.join(self.log_path, file_name)   # Where to copy img to

        # Copy the image to the home directry for plotting
        print("Sending new image")
        copyfile(src, log)
        print("New image sent.")

    def exit_app(self, save=True) :
        # Save the dataframe in its current state
        if save :
            print("Saving Progress to: ", self.csv_path)
            self.label_df.to_csv(self.csv_path)

        # Close the application
        self.app.close()
        print("\nCLOSING APP")
        exit()


    # --- Main interface loop --- #
    def main_loop(self) :
        nb_patients = len(self.label_df["patient_id"].values) # Number of patients in data set

        while self.index < nb_patients :
            """Each iteration in this loop plots and labels one patient's scan"""
            patient_id = self.label_df["patient_id"].loc[self.index]
            file_name = str(patient_id) + "_img.npy"

            # Send new image to the plotter
            image_file = os.path.join(self.img_path, file_name)
            image = np.load(image_file)
            self.app.setImage(image)

            # Ask the user if they see an artifact
            message = "Does patient {} have an artifact? [y]/n: ".format(patient_id)
            answer = input(message)

            # Process the answer and update the df (1=has artifact, 0=no artifact)
            if answer == '' or answer == 'y' or answer == 'yes' :
                print("You answered yes")
                self.label_df.at[self.index, "has_artifact"] = 1

            elif answer == 'n' or answer == 'no':
                print("You answered no")
                self.label_df.at[self.index, "has_artifact"] = 0

            else :
                print("Not a valid answer. Please hit [ENTER] for yes, or type 'y' or 'n'.")
                continue # Return to the top of the loop and ask user again

            # TODO: Save each iteration
            if self.saving == True :


            # Move to the next patient
            self.index = self.index + 1
            """ END OF LOOP """

        # If we're outside the loop, we've reached the last patient
        print("Last patient label complete. THANK YOU!")
        self.exit_app(save=True)


if __name__ == '__main__':

    print("Initializing application")
    app = LabelImageApp()

    try :
        print("Starting main app loop")
        print("Press Ctrl-C to save and exit anytime.")
        # Start the application loop
        app.main_loop()
    except KeyboardInterrupt :
        # Handle exit command
        app.exit_app(save=False)
