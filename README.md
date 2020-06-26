# ALTAR - Artifact Labelling Tool for Artifact Reduction
A cross-platform desktop application written in PyQt to help researchers manually and efficiently annotate large healthcare imaging datasets.

The application runs locally and securely connects to a remote server to access and plot one image at a time. The user can look through the 3D image and label various quantities, such as the presence of metal dental artifacts. The app loads the subsequent image while you label, so that the next image is immediately available.

## Getting Started
### Installation
1. If you do not already have Python 3.7 and the conda package manager, install them [here](https://docs.conda.io/en/latest/miniconda.html).
2. Download or clone the app repository.
```
$ git clone https://github.com/CArrowsm/label_artifacts.git
```

3. Create and activate a new conda environment for the app.
```
$ conda env create -f environment.yml
```

### App setup
