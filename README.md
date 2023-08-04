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

### Full Data Ingest and Processing Pipeline

To run the full data ingest and processing pipeline, execute: 

```
python3 collective_body_movement/data_ingest_analysis_pipeline.py
``` 

Data import can take a significant amount of time. To run a quick trial run with a reduced input, pass the argument:

```
--quick_run
```

For subsequent runs, the initial data ingest phase can be skipped to increase exeuction speed by passing the argument:
```
--skip_raw_data_ingest
```

To skip plot generation, the following option can be added:
'''
--skip_plots
'''


### Data Loading

Add data to the directory "bin/data/"; the file structure should match below, with "DATA.2023.06.26" containing subdirectories (as necessary) and csv files. 

```
bin/data/DATA.2023.06.26
```

### Data description

- 5 sessions a day for 4 days + 6 headsets
- 2 to 6 people per session
- Even numbers, paired by person
- Different people each time
- Data was collected with three experiences / chapters (need to get times)
- Phases
    - Balls falling from sky
    - Navigate through maze
    - Synchronization w/ stars

### Background on data

First scope:
- 

Future
- Saturation
- Grouping / clustering of colors
- Visual trails from movement 
    - Persistence
    - Length 
    - Size
    - Color
    - Viscosity

### Potential metrics

- Dynamic
    - Speed / movement
- Flow
    - Smoothness
    - Continuity
    - Periodicity 
- Shape of movement
    - Laban movement analysis
    - Gait recognitiion in second phase w/ maze - Period / Amplitutde of motion
- Openness / closedness
    - Hand position
- Use of space
    - Synchrony

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


