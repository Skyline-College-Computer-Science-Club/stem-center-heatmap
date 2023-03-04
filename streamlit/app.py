import pandas as pd
import streamlit as st
import os

pwd = os.getcwd()
df = pd.read_csv(pwd + "/(Enc)Data - Coded_SessionLogs.csv", index_col='Course')

# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', 20)

# Rename columns
df.columns = df.columns.str.replace('"', '')
df = df.rename(columns={'Unnamed: 0' : 'Idx'})

# Filter out 'No Sessions'
filt = (df['Services'] != 'No Sessions')
df = df[filt]

# Convert times to datetime, add 'HourIn', 'HourOut', 'Weekday' columns
df['SignInTime'] = pd.to_datetime(df['SignInTime'])
df['SignOutTime'] = pd.to_datetime(df['SignOutTime'])
df['HourIn'] = df['SignInTime'].apply(lambda x : x.hour)
df['HourOut'] = df['SignOutTime'].apply(lambda x : x.hour)
df['Weekday'] = df['SignInTime'].apply(lambda x : x.weekday())

# Filter out bad SignInTimes
filt = (df['Weekday'] <= 4) & (df['HourIn'] >= 8) & (df['HourIn'] <= 20) & (df['HourOut'] >= 8) & (df['HourOut'] <= 20)
df = df[filt]

# df['Services'].value_counts()

# Makes DataFrame M-F, 8AM-8PM
def make_df_week():
    d = {'M' : [0] * 13,
     'T' : [0] * 13,
     'W' : [0] * 13,
     'Th' : [0] * 13,
     'F' : [0] * 13,
    }
    df = pd.DataFrame(d)
    df.index += 8
    return df

# Gets the filter series that represents all passed in filters as one T/F series
def get_filter(filts):
    filt = [False] * df.shape[0]
    for f in filts:
        filt = filt | (df['Services'] == f)
    return filt

# Takes in a list of string filters (names of 'Services'), returns DataFrame
def make_df_with_filter(filts):
    # Get filt series, use it to get filtered DataFrame
    filt = get_filter(filts)
    data = df[filt]
    df_week = make_df_week()
    # Populate DataFrame using ['HourIn', 'HourOut'] and 'Weekday' values as indices
    for i in range(data.shape[0]):
        # Get hourIn and hourOut
        hourIn = data['HourIn'][i]
        hourOut = data['HourOut'][i]
        # Add 1 to df_week for each hour signed in
        for hour in range(hourIn, hourOut + 1):
            weekday = data['Weekday'][i]
            df_week.loc[hour][weekday] += 1
    return df_week


services = df['Services'].unique()
s = {}
c1, c2 = st.columns((2, 7))
with c1:
    for service in services:
        s[service] = st.checkbox(service)

ser = [service for service in services if s[service]]

# MAIN LINE - TAKES IN LIST OF SERVICES, GETS DATAFRAME
x = make_df_with_filter(['Space to Study (STEM Center)', 'Open Lab (TBA Hours)', 'In-person Tutoring (STEM Center)', 'Space to Study (MESA)', 'Virtual Tutoring', 'Workshop Attendance', 'Fabrication Lab'])
with c2:
    x = make_df_with_filter(ser)
    import seaborn as sns
    import matplotlib.pyplot as plt
    sns.set(rc={'figure.figsize':(11.7,8.27)})
    fig, ax = plt.subplots()
    sns.heatmap(x, cmap='Blues').set_title('Services')
    # sns.heatmap(x, cmap='Blues')
    st.write(fig)
# import matplotlib.pyplot as plt
# plt.show()



# fig, ax = plt.subplots()
# sns.heatmap(df_col.corr(), ax=ax)
# st.write(fig)