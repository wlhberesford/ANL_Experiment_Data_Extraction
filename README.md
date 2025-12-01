# ANL_Experiment_Data_Extraction

## Overview
Project created through Undergraduate Research Program at RPI. Data was collected from an experiment at Argonne National Lab (ANL) in summer 2025. This code can take a `.npz` file storing results and extract features needed for analysis

## Work Flow
### Data
ANL exported experiment results in `.npz` files with the following arrays and dimmensions:
* x (1,N): Time axis for experiments
* BPDwf (M,3,N): Wave form data collected from a Bipolar Diode (*pictured in blue below*). Collected for all M phase angles, at time n $\in$ N, collected via 3 different channels simulaneously 
* ictwf (M,3,N): Wave form data collected from a Integrating Current Transformer (*pictured in orange below*). Collected for all M phase angles, at time n $\in$ N, collected via 3 different channels simulaneously  
* phase (M,1): All M phase angles used durring the experiment    

![](./assets/SingleFrame.png =200x300)
*figure 1. Example Output from single phase angle*
 
![Output Graph](./assets/output.png)