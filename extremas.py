import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time as Time


def unpack(filename, npz_format = True):
    data = np.load(filename)
    keys = data.files
    
    if (npz_format) and (not keys == ['x', 'BPDwf', 'ictwf', 'phase']):
        raise TypeError
    
    return (keys,data)

def moving_average(arr, width):
    weights = np.ones(width) / width
    return np.convolve(arr, weights, mode='valid')

def frame_min_max(data, frame, channel):
    x = data["x"]          # shape (1, N_x)
    BPDwf = data["BPDwf"]  # shape (M, 3, N_y)
    
    
    # Trim x to match each waveform length separately
    x_BPD = x[0, :BPDwf.shape[2]]  # trim to BPD length
    BPD_raw = BPDwf[frame, channel, :]
    window = 201
    BPD_smooth = moving_average(BPD_raw,window)
    
    BPD_smooth_avg = BPD_smooth.mean()
    x_smooth = x_BPD[int(window/2):-int(window/2)]
    
    # Estimate half wave lengths
    above_avg = BPD_smooth[0] > BPD_smooth_avg
    max_intervals = []
    min_intervals = []    
    curr_start = -1
    curr_end= -1
    curr_index= 0
    for val in BPD_smooth:
        if (val > BPD_smooth_avg):
            if not above_avg:    
                # End of "min interval (values are less than the mean)"
                if curr_start == -1:
                    curr_start = curr_index
                else:
                    curr_end = curr_index
                    min_intervals.append((curr_start, curr_end))                    
                    curr_start = curr_index                    
        elif (val <= BPD_smooth_avg):
            if above_avg:
                # End of "max interval (values are gretor than the mean)"
                if curr_start == -1:
                    curr_start = curr_index
                    
                else:
                    curr_end = curr_index
                    max_intervals.append((curr_start, curr_end))
                    curr_start = curr_index
                    above_avg = BPD_smooth[curr_index] > BPD_smooth_avg
        
        above_avg = BPD_smooth[curr_index] > BPD_smooth_avg               
        curr_index+=1
    
        
    time_min_list = []
    time_max_list = []
    local_min_list = []
    local_max_list = []
    
            
    # Loop through min intervals
    for start, end in min_intervals:
        # find index of minimum value within interval
        local_min_idx = np.argmin(BPD_raw[start:end]) + start
        local_min_val = BPD_raw[local_min_idx]
        time_min_val = x_smooth[local_min_idx-int(window/2)]
        # store
        local_min_list.append(local_min_val)
        time_min_list.append(time_min_val)

    # Loop through max intervals
    for start, end in max_intervals:
        # find index of maximum value within interval
        local_max_idx = np.argmax(BPD_raw[start:end]) + start 
        local_max_val = BPD_raw[local_max_idx]
        time_max_val = x_smooth[local_max_idx-int(window/2)]
        # store
        local_max_list.append(local_max_val)
        time_max_list.append(time_max_val)
        
    
    return np.array(time_min_list), np.array(time_max_list), np.array(local_min_list), np.array(local_max_list)

def data_min_max(data):
    # create dataframe for results
    extremas = pd.DataFrame(columns=['Phase', 'Channel', 'Local_Max', 'Time', 'V'])
    phase = data["phase"]  # shape (M,)
    
    n_frames = len(data['BPDwf'])
    channel = 0
    start = Time.time()
    for frame in range(n_frames):
        x_mins, x_max, y_mins, y_max = frame_min_max(data, frame, channel)
        for time, v in zip(x_mins, y_mins):
            row = pd.Series({'Phase': frame, 
                             'Channel': channel, 
                             'Local_Max':False, 
                             'Time': time, 
                             'V': v})
            extremas = pd.concat([extremas, row.to_frame().T], ignore_index=True)
        for time, v in zip(x_max, y_max):
            row = pd.Series({'Phase': frame, 
                             'Channel': channel, 
                             'Local_Max':True, 
                             'Time': time, 
                             'V': v})
            extremas = pd.concat([extremas, row.to_frame().T], ignore_index=True)
        
        if(frame % 25 == 0):
            print(f"Processed frame {frame} of {n_frames} ({Time.time()-start}s)")
            
    extremas["Phase"] = extremas["Phase"].map(lambda x: phase[x])
    return extremas


if __name__ == "__main__":
    
    filename = "../Data/CoarseScan.npz"
    
    keys, data = unpack(filename, npz_format=True)
    
    extremas = data_min_max(data)
    extremas.to_csv(f"../Results/{filename.split("/")[-1].split(".")[0]}_extremas.csv", index=False)
    plt.figure(figsize=(8, 5))
    plt.scatter(extremas["Time"], extremas["V"], color="steelblue", alpha=0.7)

    plt.title("Scatter Plot of time vs v")
    plt.xlabel("Time")
    plt.ylabel("V")
    plt.grid(True)
    plt.show()
                
