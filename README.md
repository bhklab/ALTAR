# label_artifacts
label_artifacts is an application for manually labelling CT image datasets. In particular, we are interested in which patients have metal dental artifacts, but the code can easily be adapted to other questions.

## Usage
In order to start the app, simply log into the data transfer node on the HPC4Health cluster with X11 forwarding enabled.
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

Or order to see the image display GUI you must also have an X11 forwarder like xterm installed on your local machine.
