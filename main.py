"""
This uses the CSV file containing session logs and webschedule info
to represent and display the data in a DataFrame.
A DataFrame is essentially a table with rows and columns.
### It is recommended to use Jupyter Notebook to see the DataFrames. ###
"""
import pandas as pd
import os

# CSV file of session logs must be in same directory as this file
# and named '(Enc)Data - Coded_SessionLogs.csv'
cwd = os.getcwd()  # get current working directory as str
df = pd.read_csv(cwd + "/(Enc)Data - Coded_SessionLogs.csv")  # make DataFrame from CSV

# Set pandas settings - # of rows and cols to display, change it to change # of rows/cols to show
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 20)

# Rename columns for name clarity
df = df.rename(columns={'Unnamed: 0' : 'ID'})
df = df.rename(columns={'Services' : 'Service'})
df = df.rename(columns={'Period' : 'Duration'})

# Filter out 'No Sessions' - don't know what 'No Sessions' means, may have to ask Bryan
filt = (df['Service'] != 'No Sessions')
df = df[filt]

# Convert SignIn and SignOut times to 'datetime' objects so we can get attributes of the time (ex. hour)
df['SignInTime'] = pd.to_datetime(df['SignInTime'])
df['SignOutTime'] = pd.to_datetime(df['SignOutTime'])
# Add 'HourIn', 'HourOut', 'Weekday' columns
df.insert(7, 'HourIn', df['SignInTime'].apply(lambda x : x.hour))  # get hour and weekday attributes from 'datetime' obj,
df.insert(8, 'HourOut', df['SignOutTime'].apply(lambda x : x.hour))     # insert at specified column index (ex. 7)
df.insert(9, 'Weekday', df['SignInTime'].apply(lambda x : x.weekday())) # to keep desired column order

# Filter out bad SignIn, SignOutTimes - sessions not within 8AM-8PM and not weekdays
# (students signed in when STEM Center closed)
filt = (
    (df['HourIn'] >= 8) & (df['HourIn'] <= 20) &
    (df['HourOut'] >= 8) & (df['HourOut'] <= 20) & (df['Weekday'] <= 4)
)
df = df[filt]

# Reset row indices to start at 0 - needed to iterate through the DataFrame rows
df.reset_index(drop=True, inplace=True)

df['Service'].value_counts()  # just a useful function - *does nothing*


def make_df_week():
    """
    Makes an empty DataFrame representing the number of sessions for each hour 8AM-8PM, M-F.

    Returns:
        df (pandas.DataFrame): Shape (13, 5) Empty DataFrame representing
        the number of sessions for each hour 8AM-8PM, M-F, to be updated.
    """
    # Make dataframe with dictionary, 13 hours 8AM-8PM, M-F
    d = {
        'M'  : [0] * 13,
        'T'  : [0] * 13,
        'W'  : [0] * 13,
        'Th' : [0] * 13,
        'F'  : [0] * 13,
    }
    df = pd.DataFrame(d)
    df.index += 8  # add all indices (by default they start at 0) by 8 to get 8AM-8PM
    return df

# To filter the DataFrame to only sessions of the passed in service(s),
# we use a pandas.Series of T/F elements representing which sessions we want
def get_filter(services):
    '''
    Makes a boolean T/F pandas.Series (similar to list/dict) that is used
    to filter the original DataFrame of all sessions so that it only
    contains sessions that are of the passed in service(s).
    
    Args:
        services (List[str]): list of string(s) of the service(s) to be
        included in the DataFrame.
        
    Returns:
        filt (pandas.Series): A T/F Series (esentially a labeled array) that
        is True if the session is of the passed in service(s), False
        otherwise. Labeled by indices.
    '''
    filt = [False] * df.shape[0]  # boolean list of all False w/ length # of sessions
    # Update the filter for each passed in service in services
    for service in services:
        filt = filt | (df['Service'] == service)  # first iteration converts filt from list to Series obj
    return filt

# Makes week DataFrame of STEM Center hours - this function uses the two above functions
# **maybe change Friday 8AM-4PM b/c STEM Center hours)
def make_df_with_filter(services):
    """
    Makes a DataFrame with the number of sessions for each hour 8AM-8PM M-F
    for the specified type of service(s).

    Args:
        services (List[str]): list of string(s) of the services to be
        included in the DataFrame.

    Returns:
        df_week (pandas.DataFrame): A week DataFrame containing the number
        of sessions for the specified service filters.
    """
    # Get T/F Series of given service(s), use it to get filtered DataFrame
    filt = get_filter(services)  # make Series filter
    filt_df = df[filt]  # make filtered DataFrame
    filt_df.reset_index(drop=True, inplace=True)  # reset row indices to start at 0, needed to iterate over filt_df
    
    df_week = make_df_week()  # make empty week DataFrame
    
    # Add # of sessions to week DataFrame using 'HourIn', 'HourOut' and 'Weekday' values as indices
    # Loop each row in filtered df
    for i in range(filt_df.shape[0]):
        # Get hourIn, hourOut, and weekday of i'th row
        hourIn  = filt_df['HourIn'][i]
        hourOut = filt_df['HourOut'][i]
        weekday = filt_df['Weekday'][i]
        
        # Add 1 to df_week for each hour signed in from hourIn to hourOut inclusive
        # **EVENTUALLY MIGHT CHANGE TO PRECISION TO THE MINUTE**
        for hour in range(hourIn, hourOut + 1):
            df_week.loc[hour][weekday] += 1  # +1 indicates one student session at this hour and day
    return df_week

# Gets week DataFrame showing # of sessions at the hour and weekday students used the passed in service(s)
# Feel free to test out different services - keep in mind that the strings in the list must be spelled precisely
df_week = make_df_with_filter(  # passes in a *list of strings
    [
        'Space to Study (STEM Center)',
        'Open Lab (TBA Hours)',
        'In-person Tutoring (STEM Center)',
        'Space to Study (MESA)',
        'Virtual Tutoring',
        'Workshop Attendance',
        'Fabrication Lab'
    ]
)
print(df_week)

# Display DataFrame as basic "heatmap"
import seaborn as sns
sns.heatmap(df_week, cmap='Blues').set_title('# of Sessions for All Services')
# This is needed to display heatmap from terminal
import matplotlib.pyplot as plt
plt.show()