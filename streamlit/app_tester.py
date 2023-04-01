'''
Test file for streamlit web app for adding new features:
Features include Course, Department, and CRN filters and new UI
'''

import streamlit as st

import pandas as pd
import os

FILTERS = ['Service', 'Course', 'CRN', 'DEPT']  # types of filters we can filter by

# SET EVERYTHING UP FOR STREAMLIT

cwd = os.getcwd()
df = pd.read_csv(cwd + "/(Enc)Data - Coded_SessionLogs.csv")

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 20)

df.columns = [col.lower() for col in df.columns]

df = df.rename(columns={'unnamed: 0' : 'id'})
df = df.rename(columns={'"name"' : 'encrypted_name'})
df = df.rename(columns={'services' : 'service'})
df = df.rename(columns={'signintime' : 'sign_in_time'})
df = df.rename(columns={'signouttime' : 'sign_out_time'})
df = df.rename(columns={'period' : 'duration'})

filt = (df['service'] != 'No Sessions')
df = df[filt]

df['sign_in_time'] = pd.to_datetime(df['sign_in_time'])
df['sign_out_time'] = pd.to_datetime(df['sign_out_time'])
df.insert(7, 'hour_in', df['sign_in_time'].apply(lambda x : x.hour))
df.insert(8, 'hour_out', df['sign_out_time'].apply(lambda x : x.hour))
df.insert(9, 'weekday', df['sign_in_time'].apply(lambda x : x.weekday()))

filt = (
    (df['hour_in'] >= 8) & (df['hour_in'] <= 20) &
    (df['hour_out'] >= 8) & (df['hour_out'] <= 20) & (df['weekday'] <= 4)
)
df = df[filt]

df.reset_index(drop=True, inplace=True)

### Add Course, CRN, and Department columns ###

# Import registration file and do dirty cleaning - can we do it in a preliminary step??
df_reg = pd.read_csv(cwd + "/(Enc)Data - Coded_Registration.csv")
df_reg.columns = [col.lower().replace(' ', '_') for col in df_reg.columns]
df_reg['course_dept'] = df_reg['course_dept'].apply(lambda x : x.strip()) # strip white space
# Fix type inconsistencies - convert ints to string
df_reg['crn'] = df_reg['crn'].astype(str)
df_reg['course_num'] = df_reg['course_num'].astype(str)

# Merge registration and sessionlog CSV files
course_dept_col = df['course'].str.extract(r'^\[(.+)-[0-9]+\.?[0-9]\]')  # get course_dept w/ regex -> a one col df
course_num_col  = df['course'].str.extract(r'^\[.+-([0-9]+\.?[0-9])\]')  # get course_num w/ regex
df.insert(3, 'course_dept', course_dept_col)
df.insert(4, 'course_num', course_num_col)

crn_col = pd.Series(index=range(df.shape[0]), dtype=float)  # empty series

# Iteratively add CRN to Series to be added to df. Probably .merge() is faster
for idx, row in df.iterrows():
    # Get CRN if there is a course provided for tutoring in the sessionlog
    if not pd.isna(df.at[idx, 'course']):
        print(f"Index: {idx}") # TEST
        encrypted_name = row['encrypted_name']  # from sessionlogs df
        course_dept    = row['course_dept']
        course_num     = row['course_num']
        
        filt = (    ### PROBLEM WITH TYPES ONE DF HAS TYPE 'str' FOR #s, other is 'numpy.int64' - NEED CONSISTENCY
            (encrypted_name == df_reg['encrypted_name']) &
            (course_dept    == df_reg['course_dept']) &
            (course_num     == df_reg['course_num'])  # bad code here, need fix later, prob from above comment
        )
        
        # Check for errors
        try:
            crn = df_reg[filt]['crn'].iloc[0]
        except:
            # Student not registered for class he got tutoring for - we assume this class was dropped
            if df_reg[filt].shape[0] != 1:
                print("PROBLEM: THERE WASN'T ONE MATCH FOR SESSION AND STUDENT'S CRN")
            else:
                print("OTHER PROBLEM AHHHHAHHHH")
            crn = 'Dropped'
            # QUESTION: What's the difference btwn'Non-STEM Registered' and Tamarsha's case?
            # Tamarsha's edge case: dropped a class she got tutoring for -> can't get its CRN
            # What is 'Non-STEM Registered' again?
        
        crn_col[idx] = crn
        
df.insert(5, 'crn', crn_col)


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
        filt = filt | (df['service'] == service)
    return filt


def make_df_with_filter(services):
    filt = get_filter(services)
    filt_df = df[filt]
    filt_df.reset_index(drop=True, inplace=True)
    
    df_week = make_df_week()
    
    for i in range(filt_df.shape[0]):
        hour_in  = filt_df['hour_in'][i]
        hour_out = filt_df['hour_out'][i]
        weekday = filt_df['weekday'][i]
        
        for hour in range(hour_in, hour_out + 1):
            df_week.loc[hour][weekday] += 1
    return df_week


def make_df_with_streamlit_df(df):
    df.reset_index(drop=True, inplace=True)
    
    df_week = make_df_week()
    
    for i in range(df.shape[0]):
        hour_in  = df['hour_in'][i]
        hour_out = df['hour_out'][i]
        weekday = df['weekday'][i]
        
        for hour in range(hour_in, hour_out + 1):
            df_week.loc[hour][weekday] += 1
    return df_week


# Streamlit
st.set_page_config(
    page_title='STEM Center Traffic',
    page_icon='stem-center.ico',
    layout='wide'
)

st.sidebar.header('Filters:')
service = st.sidebar.multiselect(
    'Select Service(s):',
    options=df['service'].unique(),
    default=df['service'].unique()
)

course = st.sidebar.multiselect(
    'Select Course(s):',
    options=df['course'].unique(),
    default=df['course'].unique()
)

dept = st.sidebar.multiselect(
    'Select Department(s):',
    options=df['course_dept'].unique(),
    default=df['course_dept'].unique()
)

crn = st.sidebar.multiselect(
    'Select CRN(s):',
    options=df['crn'].unique(),
    default=df['crn'].unique()
)

df_selection = df.query(
    "service == @service & course == @course & course_dept == @dept & crn == @crn"
)

st.dataframe(df_selection)

week_df = make_df_with_streamlit_df(df_selection)

import seaborn as sns
import matplotlib.pyplot as plt
# sns.set(rc={'figure.figsize':(11.7,8.27)})
fig, ax = plt.subplots()
sns.heatmap(week_df, cmap='Blues').set_title('Services')
st.write(fig)