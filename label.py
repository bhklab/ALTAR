import os
import time
import numpy as np
import pandas as pd
# from PyQt5.QtWidgets import QApplication, QWidget
import pyqtgraph as pg


'''
A python script which provides a command line interface to
label the RadCure data as having dental artifacts or not.

Instructions to run the app:
1. Login to H4H on the data transfer node (your_username@h4huhndata1)
This cannot be done remotely. Ensure xterm is installed on your local machine.
$ ssh -X -p 22 username@172.27.23.173      # Data transfer node (UHN network)
2. Run this script with the command $ python label.py
---------
This implementation uses the H4H data transfer node.
TODO: Try writing something that can be run remotely.
$ ssh -X -p 10022 username@172.27.23.163   # Login node (UHN network)
$ ssh -X -p 5500 carrowsm@192.75.165.28    # Login node (remote)

matplotlib figures should appear on your local machine as you use the app.
'''


class LabelImageApp(object):
    """Command line interface to label images in a dataset."""
    def __init__(self, saving=True):
        super(LabelImageApp, self).__init__()
        self.saving = saving

        # Edit these paths according to your directory sctructure
        self.img_path = "/cluster/projects/bhklab/RADCURE/img/"                  # Path to image directory (edit this here)
        self.csv_path = "/cluster/home/carrowsm/logs/label/artifact_labels.csv"  # File containing the labels of the images
        self.tmp_path = "/cluster/home/carrowsm/logs/label/tmp.csv"              # File for temporary saving

        # Check this path exists
        self.verify_path()

        # Create the dataframe containing the labels
        self.label_df, self.index = self.init_label_df()

        # Initiate the pyqtgraph plot
        self.gui = pg.image(title="CT Scan Stack")

        # Give the user some helpful messages
        self.startup_message()



    # --- Initialization functions --- #
    def verify_path(self) :
        ''' See if the path to the data is valid'''
        if not os.access(self.img_path, os.F_OK) :
            raise ValueError("The directory {} cannot be found.".format(self.img_path))
            exit()

    def init_label_csv(self) :
        """Create an empty dataframe with the correct headers and save to csv.
           This will be appended to as the code program runs."""
        temp_df = pd.DataFrame(data={"patient_id": [], "has_artifact": []})
        temp_df.to_csv(self.csv_path)

    def init_label_df(self) :
        """ Dataframe which will store the label for each patient. If a csv with
            this data exists, load it as a pandas dataframe. Otherwise, make one.
            Also    Load the most recent state of the labeling process.
                    Find the current patient ID (this is the first NaN if the
                    CSV is not being created for the first time).
            The label_df has the following format:
        index   patient_id    has_artifact
        0       12345         1             # 1=yes, 0=no artifact
        1       23456         0
        2       45667         NaN           # Patients who have not been labeled yet get NaN status
        3       45678         NaN           # The app moves through this DF in order of index
        .        .             .
        .        .             .
        .        .             .
        """
        # Load DF if there is a CSV
        if os.access(self.csv_path, os.F_OK) :
            df = pd.read_csv(self.csv_path, dtype=str, na_values=['nan', 'NaN'], index_col="p_index")

            # Find the first artifact status which is NaN (last_valid_index gives last non-NaN)
            current_patient = df["has_artifact"].last_valid_index() + 1

        else : # If there is no CSV, make a dataframe
            # Get all the patient IDs
            ids = []
            for file in os.listdir(self.img_path) :
                ids.append(file.split("_")[0])   # Get the ID from the filename

            # Create a dataframe indexed by integers
            df = pd.DataFrame(data={"patient_id": ids, "has_artifact": np.nan}, dtype=str)
            df.index.name = "p_index"           # An ordered index for the patients
            current_patient = 0                 # Set the current patient index to 0

            # Create an emtpy CSV to append the data to each iteration
            self.init_label_csv()

        # Create a new temporary dataframe
        with open(self.tmp_path, 'w') as csv:
            csv.write(",patient_id,has_artifact\n")
            csv.close()
        return df, current_patient



    # --- Interface helper functions --- #
    def startup_message(self) :
        print("Application open. Your progress will be saved each time you give an answer.")
        if self.saving :
            print("Data will be saved to {}.".format(self.csv_path))
        else :
            print("WARNING: Results for this run will not be saved.")
        print("A GUI window should open soon with the CT scans.")
        print("Press Ctrl-C to save and exit anytime.")

    def save_answer(self, answer, index) :
        """Save the df line corresponding to the last answer to CSV"""
        if self.saving :
            i = index
            row = "{},{},{}\n".format(i,
                                    self.label_df["patient_id"].loc[i],
                                    self.label_df["has_artifact"].loc[i])
            # Save the label that was just made into a CSV.
            # This was we don't lose data if the file unexpectedly closes
            with open(self.tmp_path, 'a') as csv:
                csv.write(row)
                csv.close()
        else :
            return

    def exit_app(self) :
        """Save the entire dataframe in its current state"""
        if self.saving :
            print("\nSaving Progress to: ", self.csv_path)
            self.label_df.to_csv(self.csv_path)

        # Close the application
        self.gui.close()
        print("CLOSING APP")
        exit()


    # --- Main interface loop --- #
    def main_loop(self) :
        nb_patients = len(self.label_df["patient_id"].values) # Number of patients in data set

        while self.index < nb_patients :
            """ MAIN APP LOOP """
            """Each iteration in this loop plots and labels one patient's scan"""
            patient_id = self.label_df["patient_id"].loc[self.index]
            file_name = str(patient_id) + "_img.npy"

            # Load the new image and send to the graphing GUI
            image_file = os.path.join(self.img_path, file_name)
            image = np.load(image_file, mmap_mode="r")
            self.gui.setImage(image)
            self.gui.setCurrentIndex(60)


            # Ask the user if they see an artifact
            message = "Does patient {} have an artifact? [y]/n: ".format(patient_id)
            answer = input(message)

            # Process the answer and update the df (1=has artifact, 0=no artifact)
            if answer == '' or answer == 'y' or answer == 'yes' :
                print("You answered yes")
                self.label_df.at[self.index, "has_artifact"] = '1'

            elif answer == 'n' or answer == 'no':
                print("You answered no")
                self.label_df.at[self.index, "has_artifact"] = '0'

            else :
                print("Not a valid answer. Please hit [ENTER] for yes, or type 'y' or 'n'.")
                continue # Return to the top of the loop and ask user again


            # Save the appropriate line to the CSV
            self.save_answer(answer, self.index)


            # Move to the next patient
            self.index = self.index + 1
            """ END OF LOOP """

        # If we're outside the loop, we've reached the last patient
        print("Last patient label complete. THANK YOU!")
        self.exit_app()


if __name__ == '__main__':

    print("Initializing application")
    app = LabelImageApp(saving=True)

    try :
        # Start the application loop
        app.main_loop()
    except :
        # Handle exit command
        app.exit_app()  # Exit and save progress
