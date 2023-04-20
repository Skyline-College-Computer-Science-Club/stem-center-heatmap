from flask import Flask, render_template, request, Response, send_file, url_for

import sqlite3
import pandas as pd
import seaborn as sns

app = Flask(__name__)


# Retrieve database, configure dataframe
conn = sqlite3.connect('sessions.db')
c = conn.cursor()

query = "SELECT * FROM sessions"
df = pd.read_sql(query, conn)

# Get all services
c.execute("SELECT DISTINCT service FROM sessions")
rows = c.fetchall()
SERVICES = [row[0] for row in rows]

# Get all courses
c.execute("SELECT DISTINCT course FROM sessions")
rows = c.fetchall()
COURSES = [row[0] for row in rows]

# Get all departments
c.execute("SELECT DISTINCT course_dept FROM sessions")
rows = c.fetchall()
DEPTS = [row[0] for row in rows]


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


df_week = make_df_with_filter(  # pass in a list of strings
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


@app.route("/")
def index():
    return render_template("index.html", services=SERVICES, courses=COURSES, depts=DEPTS)
    

@app.route("/visualize")
def visualize():
    import io
    import base64
    import matplotlib
    matplotlib.use('agg')
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    import matplotlib.pyplot as plt
    import seaborn as sns
    # Weird stuff to increase resolution
    from matplotlib_inline.backend_inline import set_matplotlib_formats
    set_matplotlib_formats('svg')
    sns.set(rc={"figure.dpi":100, 'savefig.dpi':300})
    fig, ax = plt.subplots(dpi=300) # dpi=dots per inch --done resolution tweaking
    ax = sns.heatmap(df_week, cmap="YlGnBu", linewidths=0.5, annot=True, fmt="d")
    canvas = FigureCanvas(fig)
    img = io.BytesIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img, mimetype="img/png")