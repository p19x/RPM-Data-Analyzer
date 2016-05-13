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

def create_volume_time_graph(file_path, tank_type_var, date_from = None, date_to = None):
    """Creates a tank volumn in % vs time graph"""
    csv, files_exist = open_files(file_path)
    if date_from != None:
        try:
            time = csv["Train end time [local_unit_time]"] #get the time column
        except:
            time = csv["Report date"]

        print date_from
        
        date_from = pd.to_datetime(date_from)
        date_to = pd.to_datetime(date_to) + pd.DateOffset(1) 
        filtered_csv = csv[(time > date_from) & (time < date_to)] #filter out date_from to date_to
    
    else:
        filtered_csv = csv
    
    print files_exist

    if files_exist != True:
        return
    print "data analyzed"

    total_wheels = filtered_csv["Total wheels"]
    
    try:
        tank_level = filtered_csv["Product %"]
    except:
        tank_level = filtered_csv["Raw Level"]
        
    try:
        filtered_time = filtered_csv["Train end time [local_unit_time]"]
    except:
        filtered_time = filtered_csv["Report date"]
    
    voltage = pd.to_numeric(filtered_csv['Volts'])

    #find times when the control box is changed
    #counter_change = filtered_time.groupby(filtered_csv["Wheels TA"]).apply(lambda x: np.array(x))

    box_change, settings = get_setting_changes(filtered_csv, filtered_time)
    #print box_change, settings, len(box_change), len(settings)
    #print total_wheels
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    
    ax1.plot(filtered_time, tank_level, label = "tank level")
    ax2.plot(filtered_time, voltage, color='Red', label = "voltage", alpha=0.5)
    [ax1.axvline(x=i, ls='--', lw=2.0) for i in box_change]
    [ax1.annotate('{0} x {1}'.format(s[0],s[1]), xy=(box_change[i], 15)) for i, s in enumerate(settings)]
    ax1.legend(loc=0)
    ax2.legend(loc=0)
    plt.title("Tank level and voltage over time")
    ax1.set_ylabel("Tank Level", color='Blue')
    ax2.set_ylabel("Voltage", color='Red')
    plt.xlabel("Time")
    plt.show()

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

def fit_line(x, y):
    """Return slope, intercept of best fit line."""
    X = sm.add_constant(x)
    model = sm.OLS(y, X, missing='drop') # ignores entires where x or y is NaN
    fit = model.fit()
    print "slope and intercept found"
    return fit.params[1], fit.params[0] # could also return stderr in each via fit.bse

def regress_line(x, m, b):
    """Return an array which plots the best fit line"""
    X = np.array([x.min(),x.max()])
    Y = m * X + b
    print "best fit line found"
    return X, Y

def make_dataframe(file_path, date_from, date_to):
    """Returns the filtered dataframe from a file"""
    csv, files_exist = open_files(file_path)

    print files_exist
    # if no files selected, exit function
    if files_exist != True:
        return

    try:
        time = csv["Train end time [local_unit_time]"] #get the time column
    except:
        time = csv["Report date"]

    date_from = pd.to_datetime(date_from)
    date_to = pd.to_datetime(date_to) + pd.DateOffset(1) 
    filtered_csv = csv[(time > date_from) & (time < date_to)] #filter out date_from to date_to
    
    if date_from > date_to:
        tkMessageBox.showinfo("DateWarning","Date to must be later than date from")
        return

    print "time filter successful for " + str(date_from) + " to " + str(date_to)
    
    try:
        filtered_time = filtered_csv["Train end time [local_unit_time]"]
    except:
        filtered_time = filtered_csv["Report date"] #get time column after filter

    filtered_csv = filtered_csv[filtered_csv["Wheels TA"] < 100] #filters out any abnormal data

    total_wheels = filtered_csv["Total wheels"]
    
    if filtered_csv['Last Train Direction'].isnull().any() == False:
        grouped_wheels = total_wheels.groupby(filtered_csv['Last Train Direction']) #divide the directions to calculate the wheel count differences separately
        filtered_csv['wheel_count_diff'] = grouped_wheels.diff() * -1 # calculates the wheel count
        filtered_csv['wheel_count_diff'] = filtered_csv['wheel_count_diff'].shift(-1)
    else:
        grouped_wheels = total_wheels
        filtered_csv['wheel_count_diff'] = grouped_wheels.diff() * -1
        filtered_csv['wheel_count_diff'] = filtered_csv['wheel_count_diff'].shift(-1)
    
    
    print "wheel count calculation successful"
    return filtered_csv, files_exist

def process_csv(filtered_csv, tank_type_var):
    filtered_csv['wheel_count'] = filtered_csv['wheel_count_diff'].cumsum() #find the running total of wheel count 
    filtered_csv['times_activated'] = filtered_csv['wheel_count']/filtered_csv['Wheels TA'] #find the running total of times activated
    filtered_csv['seconds_activated'] = filtered_csv['times_activated'] * filtered_csv['Pump time (sec)'] #find the running total of seconds activated
    seconds_activated = filtered_csv['seconds_activated'] 
    
    try:
        tank_level = filtered_csv["Product %"]
    except:
        tank_level = filtered_csv["Raw Level"] #get the tank level in percentages

    if tank_type_var == "std":
        full_tank = 370.19
    else: full_tank = 351.12
    filtered_csv["product_volume"] = tank_level/100*full_tank
    product_volume = filtered_csv["product_volume"]
    
    #filtered_csv = filtered_csv.replace(0, np.nan)
    
    return filtered_csv

def calculate_consumption(date_from, date_to, tank_type_var, file_path1, file_path2 = None):
    dataframe1, files_exist = make_dataframe(file_path1, date_from, date_to)
    if file_path2 != None:
        dataframe2, files_exist = make_dataframe(file_path2, date_from, date_to)
        frames = [dataframe1, dataframe2]
        df = pd.concat(frames)
    else:
        df = dataframe1

    if files_exist != True:
        return
    
    try:
        time = "Train end time [local_unit_time]" #get the time column
        df = df.sort(columns=time)
    except:
        time = "Report date"
        df = df.sort(columns=time)
    
    #df[df['wheel_count_diff'] > 10000]['wheel_count_diff'].diff()
    
    processed_df = process_csv(df, tank_type_var)
    
    processed_df['Volts'] = pd.to_numeric(processed_df['Volts'])
    
    file_output = open("C:\My Documents\Output Test\RPM Output Calc\\summary.csv", "wb")
    processed_df.to_csv(file_output)
    file_output.close() ##write the df after calc to csv
    
    voltage = processed_df['Volts'].mean()
    temp = processed_df['T amb (C)'].mean()
    #print "voltage and temperature are", voltage, temp
    
    total_wheels = processed_df['wheel_count_diff'].sum()
    wheels_per_activation = processed_df['Wheels TA'].dropna().unique() #find the different wheel settings in the period
    seconds_per_pump = processed_df['Pump time (sec)'].dropna().unique() #find the different seconds setting in the period
    
    #processed_df = processed_df.replace(np.nan, 0)
    #processed_df = processed_df.replace(np.inf, 0)
    
    
    seconds_activated = processed_df['seconds_activated']
    product_volume = processed_df["product_volume"]
    smask = np.isfinite(product_volume) #connects the lines with nan values for product volume
    slope, intercept = fit_line(seconds_activated, product_volume) ###need to remove outliers before slope calculation
    
    volume_bgn = intercept
    volume_end = processed_df['seconds_activated'].max() * slope + intercept
    
    print wheels_per_activation, seconds_per_pump
    if len(wheels_per_activation) == 1 and len(seconds_per_pump) == 1:
        wheels = wheels_per_activation[0]
        seconds = seconds_per_pump[0]
        litre_per_kaxles = -slope*1000/wheels_per_activation[0]*seconds_per_pump[0]
    if len(wheels_per_activation) != 1 or len(seconds_per_pump) != 1:
        wheels = wheels_per_activation[0]
        seconds = seconds_per_pump[0]
        litre_per_kaxles = -slope*1000/wheels_per_activation[0]*seconds_per_pump[0]
    
    ctrl_box = str(seconds) + ' x ' + str(wheels)
    
    print "The output according to RPM is", litre_per_kaxles, "L/1000axles"


    X, Y = regress_line(seconds_activated, slope, intercept)
    plt.title("Product Volume vs Seconds of Pump Activated " + date_from + "-" + date_to)
    plt.xlabel("Seconds of Pump Activated (s)")
    plt.ylabel("Product Volume (L)")
    plt.figtext(0.3,0.8, str(litre_per_kaxles) + " L/1000axles")
    plt.figtext(0.8,0.8, ctrl_box)
    plt.figtext(0.65,0.7, "%d wheels passed\nVolume: %.1f to %.1f" %(total_wheels, volume_bgn, volume_end))
    plt.plot(seconds_activated[smask], product_volume[smask])
    plt.plot(X,Y)
    plt.show()

    return litre_per_kaxles, voltage, temp, ctrl_box

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
