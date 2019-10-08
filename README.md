# label_artifacts
label_artifacts is an application for manually labelling CT image datasets. In particular, we are interested in which patients have metal dental artifacts, but the code can easily be adapted to other questions.

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
If you want to change the directories from which images are retrieved, or the location where your labels are saved, edit lines 35-37 in `label.py`:
```python
self.img_path = "/cluster/projects/bhklab/RADCURE/img/"                  # Path to image directory (edit this here)
self.csv_path = "/cluster/home/carrowsm/logs/label/artifact_labels.csv"  # File containing the labels of the images
```
