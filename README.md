# CAMED - noCEP

This project is a CAMED (Contextual Anomaly Mitigation for Event-Driven Systems) baseline that inputs raw data streams directly to the UL model. (CAMED without CEP)

It's used to compares results with CAMED, employing the CEP pre-filter.

# Project structure

```
camed_noCEP/
├── camed_noCEP.py                          # NoCEP version of CAMED
├── net_helper.py                           # Helper to network interfaces selection
├── model/
│   └── model.pickle                        # The machine learn model pickle file
├── camed_noCEP.sh.sh                       # Bash script to run CAMED noCEP
├── start_nmon.sh                           # Bash script to run nmon and collect the system performance statistics
├── requirements.txt                        # Required python libraries
├── README.md                               # This file
```

# Installation

## Dependences

    - Python 3.12 or higher
    - nmon

## How to install

    $ virtualenv venv
    $ source venv/bin/activate
    $ pip3 install -r requirements.txt

# How to execute

### Requirements:
You must have a docker network running and configured in the project's dockerfile (We define the creation of the network in the nmon script for redundancy purposes)
    
## Running

    $ sudo su
    $ source venv/bin/activate
    $ ./start_nmon.sh

### Disclamer: Run nmon script in exclusive terminal with root privileges

## 1. Execte as a bash script:
    $ ./camed_noCEP.sh

## 2. Execte as a python script:
    $ export RUN=1                          # Change this value with your desired RUN value
    $ python3 camed_noCEP.py