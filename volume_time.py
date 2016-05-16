import matplotlib.pyplot as plt

from Tkinter import *
import pandas as pd
import statsmodels.api as sm
import numpy as np
import csv
import global_variables
import tkMessageBox

files_exist = None

def open_files(file_path):
    files_exist = True
    try:
        if "Daily" in file_path:
            #print "Daily"
            csv = pd.read_csv(file_path, parse_dates = [0,2], infer_datetime_format = True) 
        else:
        #if "Train" in file_path:
            print "Train"
            csv = pd.read_csv(file_path, parse_dates = [0,2], infer_datetime_format = True)
    except IOError:
        tkMessageBox.showinfo("FileWarning","Please select file(s) first")
        files_exist = False
        return
    print "file opened", files_exist
    return csv, files_exist

def create_volume_time_graph(tank_type_var, file_path, file_path2 = None, date_from = None, date_to = None):
    """Creates a tank volumn in % vs time graph"""
    csv1, files_exist = open_files(file_path)

    if file_path2 != None:
        csv2, files_exist = open_files(file_path2)
        frames = [csv1, csv2]
        csv = pd.concat(frames)

    try:
        time = "Train end time [local_unit_time]" #get the time column
        csv = csv.sort(columns=time)
    except:
        time = "Report date"
        csv = csv.sort(columns=time)

    print files_exist

    if files_exist != True:
        return
    print "data analyzed"

    total_wheels = csv["Total wheels"]
    
    try:
        tank_level = csv["Product %"]
    except:
        tank_level = csv["Raw Level"]
    tank_level_mask = np.isfinite(tank_level)


    #find times when the control box is changed
    #counter_change = filtered_time.groupby(filtered_csv["Wheels TA"]).apply(lambda x: np.array(x))

    box_change, settings = get_setting_changes(csv, get_time(csv))
    #print box_change, settings, len(box_change), len(settings)
    #print total_wheels
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    ax1.plot(get_time(csv)[tank_level_mask], tank_level[tank_level_mask], label = "tank level")
    
    if file_path2 != None:
        voltage1 = pd.to_numeric(csv1['Volts'])
        voltage2 = pd.to_numeric(csv2['Volts'])
        ax2.plot(get_time(csv1), voltage1, color='Red', label = "voltage1", alpha=0.5)
        ax2.plot(get_time(csv2), voltage2, color='Darkred', label = "voltage2", alpha=0.5)
    else:
        voltage = pd.to_numeric(csv['Volts'])
        ax2.plot(get_time(csv), voltage, color='Red', label = "voltage", alpha=0.5)
    [ax1.axvline(x=i, ls='--', lw=2.0) for i in box_change]
    [ax1.annotate('{0} x {1}'.format(s[0],s[1]), xy=(box_change[i], 15)) for i, s in enumerate(settings)]
    ax1.legend(loc=0)
    ax2.legend(loc=0)
    plt.title("Tank level and voltage over time")
    ax1.set_ylabel("Tank Level", color='Blue')
    ax2.set_ylabel("Voltage", color='Red')
    ax2.set_ylim(0,15)
    plt.xlabel("Time")
    plt.show()

def get_time(df):
    try:
        filtered_time = df["Train end time [local_unit_time]"]
    except:
        filtered_time = df["Report date"]
    return filtered_time

def get_setting_changes(filtered_csv, filtered_time):
    filtered_csv['value_grp_w'] = (filtered_csv["Wheels TA"].diff(1) != 0).astype('int').cumsum()
    counter_change = filtered_time.groupby(filtered_csv['value_grp_w']).first()

    filtered_csv['value_grp_s'] = (filtered_csv["Pump time (sec)"].diff(1) != 0).astype('int').cumsum()
    seconds_change = filtered_time.groupby(filtered_csv['value_grp_s']).first()

    print counter_change
    print seconds_change
    box_change = sorted(list(set(list(counter_change) + (list(seconds_change)))))
    wheel_settings = [filtered_csv[filtered_time == box_c].loc[:,"Wheels TA"].values[0] for box_c in box_change]
    seconds_settings = [filtered_csv[filtered_time == box_c].loc[:,"Pump time (sec)"].values[0] for box_c in box_change]
    
    settings = zip(wheel_settings, seconds_settings)
    #print [filtered_time[box_c]["Wheels TA"] for box_c in box_change]
    return box_change, settings



# full_list = []

# data_file = "C:\My Documents\Output Test\CP\Laggan\\Train_Report_Laggan 805.csv"
# # data_file2 = "C:\My Documents\Output Test\CP\Thomp27.3\Jan 12\\Daily_Report_L01099_from_10-14-2015 12-00-00 AM_to_1-12-2016 12-00-00 AM.csv"
# create_volume_time_graph(data_file)

# #calculate_consumption("12/22/2015","1/11/2016", data_file)

# with open("C:\My Documents\Output Test\CP\Laggan\\laggan 805.csv") as csvfile:
#    csvf = csv.reader(csvfile)
#    for row in csvf:
#        date_from, date_to = row
#        #calculate_consumption(date_from, date_to, data_file)
#        litre_per_kaxles, voltage, temp, ctrl_box = calculate_consumption(date_from, date_to, data_file)
#        info_list = [date_from, date_to, litre_per_kaxles, voltage, temp, ctrl_box]
#        full_list.append(info_list)


# with open("C:\My Documents\Output Test\CP\Laggan\\full_list_laggan 805.csv", 'wb') as csvfile:
#    csvw = csv.writer(csvfile)
#    for row in full_list:
#        csvw.writerow(row)
