import streamlit as st

import pandas as pd
import os

# SET EVERYTHING UP FOR STREAMLIT
cwd = os.getcwd()
df = pd.read_csv(cwd + "/(Enc)Data - Coded_SessionLogs.csv")

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 20)

df = df.rename(columns={'Unnamed: 0' : 'ID'})
df = df.rename(columns={'Services' : 'Service'})
df = df.rename(columns={'Period' : 'Duration'})

filt = (df['Service'] != 'No Sessions')
df = df[filt]

df['SignInTime'] = pd.to_datetime(df['SignInTime'])
df['SignOutTime'] = pd.to_datetime(df['SignOutTime'])
df.insert(7, 'HourIn', df['SignInTime'].apply(lambda x : x.hour))
df.insert(8, 'HourOut', df['SignOutTime'].apply(lambda x : x.hour))
df.insert(9, 'Weekday', df['SignInTime'].apply(lambda x : x.weekday()))

filt = (
    (df['HourIn'] >= 8) & (df['HourIn'] <= 20) &
    (df['HourOut'] >= 8) & (df['HourOut'] <= 20) & (df['Weekday'] <= 4)
)
df = df[filt]

df.reset_index(drop=True, inplace=True)

def make_df_week():
    d = {
        'M'  : [0] * 13,
        'T'  : [0] * 13,
        'W'  : [0] * 13,
        'Th' : [0] * 13,
        'F'  : [0] * 13,
    }
    df = pd.DataFrame(d)
    df.index += 8
    return df

def get_filter(services):
    filt = [False] * df.shape[0]
    for service in services:
        filt = filt | (df['Service'] == service)
    return filt

def make_df_with_filter(services):
    filt = get_filter(services)
    filt_df = df[filt]
    filt_df.reset_index(drop=True, inplace=True)
    
    df_week = make_df_week()
    
    for i in range(filt_df.shape[0]):
        hourIn  = filt_df['HourIn'][i]
        hourOut = filt_df['HourOut'][i]
        weekday = filt_df['Weekday'][i]
        
        for hour in range(hourIn, hourOut + 1):
            df_week.loc[hour][weekday] += 1
    return df_week


st.set_page_config(
    page_title='STEM Center Traffic',
    page_icon='stem-center.ico',
    layout='wide'
)

st.dataframe(df)

st.sidebar.header('Filters:')
service = st.sidebar.multiselect(
    'Select Service(s)',
    options=df['Service'].unique(),
    default=df['Service'].unique()
)