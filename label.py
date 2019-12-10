import os
import time
import numpy as np
import pandas as pd
import pyqtgraph as pg

import warnings
warnings.filterwarnings("ignore")

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

A pyqtgraph GUI should appear on your local machine as you use the app.
'''


class LabelImageApp(object):
    """Command line interface to label images in a dataset."""
    def __init__(self, saving=True, img_widget=None, sftp_client=None):
        super(LabelImageApp, self).__init__()
        self.saving = saving

        self.sftp = sftp_client

        ## EDIT THESE FOR YOUR IMAGE QUOTA ##
        self.start_index = 0        # Index to start at. Program will ignore everything before this
        self.stop_index  = 458      # Index to stop at. Program will ignore everything after this.
        ## ------------------------------- ##

        ##  Edit these paths according to your directory sctructure ##
        # self.img_path = "/cluster/projects/bhklab/RADCURE/img/"                  # Path to image directory
        self.img_path = "/cluster/projects/radiomics/Temp/RADCURE-npy/img"
        self.csv_path = "/cluster/home/carrowsm/logs/label/artifact_labels.csv"  # File containing the labels of the images
        # self.tmp_path = "/cluster/home/carrowsm/logs/label/tmp.csv"
        self.tmp_path = "tmp.csv"            # File for temporary saving
        ## -------------------------------------------------------- ##

        # Check this path exists
        # self.verify_path()

        # Create the dataframe containing the labels
        # self.label_df, self.index = self.init_label_df()
        self.label_df, self.index = self.load_remote_df()


        # Initiate the pyqtgraph plot
        # self.gui = pg.image(title="CT Scan Stack")
        #
        # # Give the user some helpful messages
        # self.startup_message()



    # --- Initialization functions --- #
    def verify_path(self) :
        ''' See if the path to the data is valid'''
        if not os.access(self.img_path, os.F_OK) :
            raise ValueError("The directory {} cannot be found.".format(self.img_path))
            exit()

    def init_label_csv(self) :
        """Create an empty dataframe with the correct headers and save to csv.
           This will be appended to as the program runs."""
        temp_df = pd.DataFrame(data={"patient_id": [], "has_artifact": [], "a_slice":[]})
        temp_df.to_csv(self.csv_path)

    def load_remote_df(self) :
        """ Similar to init_label_df, but uses sftp"""
        remote_csv = self.sftp.open(self.csv_path, "r", 32768)
        df = pd.read_csv(remote_csv, index_col="p_index", dtype=str, na_values=['nan', 'NaN', ''])
        remote_csv.close()

        # Create a new temporary CSV file
        # Data will be appended to this every iteration
        # with self.sftp.open(self.tmp_path, "w") as csv:
        #     csv.write("p_index,patient_id,has_artifact,a_slice\n")
            # csv.close()
        # Local temp file
        with open(self.tmp_path, "w") as csv :
            csv.write("p_index,patient_id,has_artifact,a_slice\n")

        try :
            # Find the first artifact status which is NaN (last_valid_index gives last non-NaN)
            df_restrict = df.loc[self.start_index : self.stop_index]  # Restrict dataframe (both start and stop are included)
            current_patient = df_restrict["has_artifact"].last_valid_index() + 1
        except TypeError :
            current_patient = self.start_index # If the CSV is empty, start at 1st patient

        return df, current_patient



    def init_label_df(self) :
        """ Dataframe which will store the label for each patient. If a csv with
            this data exists, load it as a pandas dataframe. Otherwise, make one.
            Also    Load the most recent state of the labeling process.
                    Find the current patient ID (this is the first NaN if the
                    CSV is not being created for the first time).
            The label_df has the following format:
        index   patient_id    has_artifact   a_slice
        0       12345         1              98      # 2=strong, 1=weak, 0=no artifact
        1       23456         0              NaN     #
        2       45667         NaN                    # Patients who have not been labeled yet get NaN status
        3       45678         NaN                    # The app moves through this DF in order of index
        .        .             .
        .        .             .
        .        .             .
        """
        # Load DF if there is a CSV
        if os.access(self.csv_path, os.F_OK) :
            df = pd.read_csv(self.csv_path, index_col="p_index", dtype=str, na_values=['nan', 'NaN', ''])

            try :
                # Find the first artifact status which is NaN (last_valid_index gives last non-NaN)
                df_restrict = df.loc[self.start_index : self.stop_index]  # Restrict dataframe (both start and stop are included)
                current_patient = df_restrict["has_artifact"].last_valid_index() + 1
            except TypeError :
                current_patient = self.start_index # If the CSV is empty, start at 1st patient

        else : # If there is no CSV, make a dataframe
            # Get all the patient IDs
            ids = []
            for file in os.listdir(self.img_path) :
                ids.append(file.split("_")[0])   # Get the ID from the filename

            # Create a dataframe indexed by integers
            df = pd.DataFrame(data={"patient_id": ids, "has_artifact": np.nan, "a_slice":np.nan}, dtype=str)
            df.index.name = "p_index"           # An ordered index for the patients
            current_patient = self.start_index  # Set the current patient index to 0

        # Create a new temporary CSV file
        # Data will be appended to this every iteration
        with open(self.tmp_path, 'w') as csv:
            csv.write("p_index,patient_id,has_artifact,a_slice\n")
            csv.close()

        return df, current_patient



    # --- Interface helper functions --- #
    def startup_message(self) :
        print("Application open.")
        if self.saving :
            print("Data will be saved to {} Once you close the program.".format(self.csv_path))
            print("Data will also be saved to {} every time you label a scan.".format(self.tmp_path))
        else :
            print("WARNING: Results for this run will not be saved.")
        print("A GUI window should open soon with the CT scans.")
        print("###-----------------------------------------###")
        print("To close and save your progress, FIRST close the GUI window\n"
              +"(with the 'x' button) and then press Ctrl-C in the command line.")
        print("###-----------------------------------------###")

    def save_answer(self, index) :
        """Save the df line corresponding to the last answer to CSV"""
        if self.saving :
            i = index
            row = "{},{},{},{}\n".format(i,
                                      self.label_df["patient_id"].loc[i],
                                      self.label_df["has_artifact"].loc[i],
                                      self.label_df["a_slice"].loc[i])
            # Save the label that was just made to a local CSV.
            # This way we don't lose data if the file unexpectedly closes
            with open(self.tmp_path, "a") as csv :
                csv.write(row)
        else :
            return

    def exit_app(self) :
        """Save the entire dataframe in its current state"""
        if self.saving :
            print("\nSaving Progress to: ", self.csv_path)

            with self.sftp.open(self.csv_path, "w") as f:
                f.write(self.label_df.to_csv(na_rep='nan'))

        # Close the application
        # self.gui.close()
        # print("\nCLOSING APP")
        # exit()


    def normalize(self, img, MIN=-1000.0, MAX=1000.0) :
        # Normalize the image (var = 1, mean = 0)
        img = img.astype(np.float32)
        img = np.clip(img, MIN, MAX)
        img = (img - MIN) / (MAX - MIN)
        return img

    def process_result(self, result, index=None, slice=None) :
        # if index < self.stop_index+1 :
        if result == "s" :
            self.label_df.at[index, "has_artifact"] = '2'
        elif result == "w" :
            self.label_df.at[index, "has_artifact"] = '1'
        elif result == "n" :
            self.label_df.at[index, "has_artifact"] = '0'

        self.label_df.at[index, "a_slice"] = str(slice)

        # Save this label to a csv
        print("Saving answer")
        self.save_answer(index)

        # else :
        #     # If we're outside the loop, we've reached the last patient
        #     print("Last patient label complete. THANK YOU!")
        #     self.exit_app()




'''
if __name__ == '__main__':

    print("Initializing application")
    app = LabelImageApp(saving=True)

try :
    # Start the application loop
    app.main_loop()

except KeyboardInterrupt :
    # Handle exit command
    print("\nApp exited from command line.")
    app.exit_app()  # Exit and save progress
except :
    # Handle unexpected issues
    print("Something Went Wrong.")
    app.exit_app()  # Exit and save progress
'''
