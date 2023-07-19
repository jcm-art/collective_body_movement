Collective Body
================

# Introduction

TBD

# Usage

## Setup

To set up the data analysis tools for collective body, first run setup.sh. This will install the necessary python packages and create the necessary directories.

```
./setup.sh
```

Second, activate the virutal environment.

```
source cbenv/bin/activate
```

## Usage

### Data Loading

Add data to the directory "bin/data/"; the file structure should match below, with "DATA.2023.06.26" containing subdirectories (as necessary) and csv files. 

```
bin/data/DATA.2023.06.26
```

### Data cleaning

Run the following command to clean the data and generate a database of raw movements.

```
python3 collective-body-movement/preprocessing/raw_movement_data_cleaning.py
```

### Raw data plotting

Run the following command to plot raw data movement.

```
python3 collective-body-movement/analysis/raw_movement_data_plotting.py
```
