import os
import io
import zipfile
import datetime
from datetime import timedelta, date

from sqlalchemy import engine_from_config, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from hornstone.alchemy import Base
import us
from revaers.models import Data, VaxData
from revaers.parser import parse_csv
from revaers.parser import parse_csvfile
from revaers.parser import parse_vaxfile

import numpy as np
import plotly.io as pio
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
# import cufflinks
import matplotlib.animation as animation
import matplotlib

plt.style.use('dark_background')
Writer = animation.writers['ffmpeg']
writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)

one_day = timedelta(days=1)
today = date.today()


data_csv_fieldnames = [
    'VAERS_ID', 'RECVDATE', 'STATE', 'AGE_YRS', 'CAGE_YR',
    'CAGE_MO', 'SEX', 'RPT_DATE', 'SYMPTOM_TEXT', 'DIED',
    'DATEDIED', 'L_THREAT', 'ER_VISIT', 'HOSPITAL',
    'HOSPDAYS', 'X_STAY', 'DISABLE', 'RECOVD', 'VAX_DATE',
    'ONSET_DATE', 'NUMDAYS', 'LAB_DATA', 'V_ADMINBY',
    'V_FUNDBY', 'OTHER_MEDS', 'CUR_ILL', 'HISTORY', 'PRIOR_VAX',
    'SPLTTYPE', 'FORM_VERS', 'TODAYS_DATE', 'BIRTH_DEFECT',
    'OFC_VISIT', 'ER_ED_VISIT', 'ALLERGIES'
    ]


def get_zip_file(year=2021, month=None, day=None):
    filename = "{}VAERSData.zip".format(year)
    if month is not None:
        filename = "{}VAERSData-{:02d}-{:02d}.zip".format(year, month, day)
    return filename



dburl = 'postgresql+psycopg2://dbadmin@localhost/revaers'
settings = {'sqlalchemy.url': dburl}
engine = engine_from_config(settings)
Base.metadata.create_all(engine)
Session = sessionmaker()
Session.configure(bind=engine)

all_csv_dates = [
    (2, 19),
    (2, 26),
    # (3, 5),
    (3, 12),
    (3, 19),
    (3, 26),
    (4, 2),
    (4, 9),
    (4, 16),
    (4, 23),
    (4, 30),
    (5, 7),
    (5, 14),
    (5, 21),
    ]

csv_dates = [
    (5, 14),
    (5, 21),
    ]
    


csv_directory = '/freespace/home/umeboshi/mscourtstuff/covid-19/reports'

s = Session()

def get_csv_files(dates=csv_dates, root=csv_directory):
    for month, day in dates:
        filename = get_zip_file(2021, month, day)
        csvdate = datetime.date(2021, month, day)
        filename = os.path.join(csv_directory, get_zip_file(2021, month, day))
        # print(filename, os.path.isfile(filename))
        with zipfile.ZipFile(filename) as zfile:
            # xsbreakpoint()
            print(zfile, zfile.filelist)
            with io.TextIOWrapper(zfile.open('2021VAERSDATA.csv'),
                                  errors='replace') as csvfile:
                parse_csvfile(csvfile, csvdate, s)
            with io.TextIOWrapper(zfile.open('2021VAERSVAX.csv'),
                                  errors='replace') as csvfile:
                print("parsing vaxfile", month, day)
                parse_vaxfile(csvfile, s)
        

def get_covid_reports(session):
    return session.query(VaxData).filter_by(vax_type="COVID19").join(Data)

def get_death_times(session):
    dead = session.query(Data).filter_by(died=True)
    days = dict()
    for patient in dead:
        if patient.datedied and patient.vax_date:
            days[patient.vaers_id] = patient.datedied - patient.vax_date
    return days





def make_data_frame(query):
    return pd.read_sql(query.statement, query.session.bind)


# query = s.query(Data, VaxData).join(VaxData)
# query = query.filter(VaxData.vax_type == 'COVID19')

def make_cvquery(session, enddate):
    query = session.query(Data, VaxData).join(VaxData)
    query = query.filter(VaxData.vax_type == 'COVID19')
    query = query.filter(Data.recvdate <= enddate)
    return query

def get_vax_manus(session, enddate):
    query = make_cvquery(session, enddate)
    query = query.distinct(VaxData.vax_manu).group_by(VaxData.vax_manu,
                                                      Data.vaers_id,
                                                      VaxData.vaers_id)
    return [r.VaxData.vax_manu for r in query]


def get_vtype_counts(session, enddate):
    vtypes = get_vax_manus(session, enddate)
    counts = dict()
    for manu in vtypes:
        query = make_cvquery(session, enddate)
        query = query.filter(VaxData.vax_manu == manu)
        counts[manu] = query.count()
    return counts



enddate = date(2021, 1, 1)

fig, ax = plt.subplots()
#fig = plt.figure()
frames = list()
index_date = enddate
fcount = 1
while index_date <= today:
    counts = get_vtype_counts(s, index_date)
    k, v = counts.keys(), counts.values()
    #ax = matplotlib.axes.Axes(fig, fig.patch)
    #px = plt.bar(counts.keys(), counts.values(), title=index_date)
    #.title(index_date)
    ax.set_title(index_date)
    px = ax.bar(k, v)
    print(counts)
    frames.append(px)
    index_date += one_day
    fcount += 1
    
ani = animation.ArtistAnimation(fig, frames, interval=50, repeat_delay=2000)
ani.save('bars.mp4', writer=writer)

# df = make_data_frame(query)

#im_ani = animation.ArtistAnimation(fig2, ims, interval=50, repeat_delay=3000,
#                                   blit=True)
#im_ani.save('im.mp4', writer=writer)

# events 34187
# deaths 1974

# events 40453
# deaths 2170

# events 46279
# deaths 2261
# jj 5327

# pre-update 4-23
# events 57774
# deaths 2526


# pre-update 4-30
# events 75517
# deaths 3117

# pre-update 5-7
# events 108361
# deaths 3484

# pre-update 5-14
# 5-7 update goes back to 4-30
# events 146853
# deaths 3806

# pre-update 5-21
# 5-7 update goes back to 5-14
# events 182869
# deaths 4108


