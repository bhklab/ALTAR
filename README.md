# label_artifacts - A Dental Artifact Labelling Application
label_artifacts is an application for manually labelling CT image datasets. In particular, we are interested in which patients have metal dental artifacts, but the code can easily be adapted to label other variables.

## Installation for BHKLab
Clone this repository to a directory under your H4H `home` directory with
```bash
git clone https://github.com/CArrowsm/label_artifacts.git
```
Change line 40 in `label.py` to point the location of `artifact_labels.csv`. Results will be saved here every time you close the application. For example, change line 40 in `label.py` to:
```python
self.csv_path = "/cluster/home/username/logs/artifact_labels.csv"  # File containing the labels of the images
```
 This file can be moved anywhere, as long as you change this line accordingly.

 You will also have to edit line 40 in `label.py`, which points to a temporary CSV called `tmp.csv`. This file can also be anywhere you would like.`tmp.csv` will save data after you label each patient. If the app crashes unexpectedly and does not save successfully to `artifact_labels.csv`, you can go into `tmp.csv` to recover your work.

## Usage
In order to start the app, simply log into the data transfer node on the HPC4Health cluster with X11 forwarding enabled. This has only been tested on the UHN corporate-wireless network.
```bash
$ ssh -X -p 22 username@172.27.23.173
```
and run the main label.py script from the command line.
```bash
$ python label.py
```
## Dependencies
The app should be run with python3 and uses the following libraries:
* os
* time
* numpy
* pandas
* pyqtgraph

Or order to see the image display GUI you must also have an X11 forwarder like [xterm](http://xquartz.macosforge.org/landing/) installed on your local machine.

## Edits
If you want to change the directories from which images are retrieved, or the location where your labels are saved, edit lines 40-40 in `label.py`:
```python
self.img_path = "/cluster/projects/bhklab/RADCURE/img/"                  # Path to image directory (edit this here)
self.csv_path = "/cluster/home/carrowsm/logs/label/artifact_labels.csv"  # File containing the labels of the images
```
