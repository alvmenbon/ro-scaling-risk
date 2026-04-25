# RO Scaling Risk Estimator

A tool for estimating scaling risk in reverse osmosis membranes 
during conceptual design of seawater desalination plants.

## The Problem

In early design phases, engineers often lack a real water analysis 
for the plant site, or have a single point-in-time sample that does 
not reflect seasonal variability. Designing with a single water 
quality value leads to undersizing the antiscalant system or setting 
an aggressive recovery for critical conditions.

## What This Tool Does

Given the geographic coordinates of a coastal desalination plant 
and a target recovery rate, this tool:

- Retrieves historical temperature and salinity data from 
  Copernicus Marine Service (CMEMS)
- Reconstructs the full ionic profile of the feed water
- Calculates scaling indices along the RO train for different 
  recovery rates
- Shows how scaling risk varies throughout the year

## Who Is This For

Process engineers at EPC companies or consultancies working on 
seawater desalination projects in early design or tender phases.

## Scope and Limitations

Works well for open ocean and semi-enclosed seas 
(Mediterranean, Red Sea, Persian Gulf).
Less accurate in coastal areas with significant freshwater input.
Not applicable to brackish water or inland sources.

## Project Status

🚧 Under construction

## Tech Stack

- Python 3.10+
- copernicusmarine (CMEMS API)
- numpy, scipy
- matplotlib / plotly

## Author

Álvaro Mendoza — Process Engineer, Water Sector  
[www.linkedin.com/in/alvaro-mendoza-bonilla]
