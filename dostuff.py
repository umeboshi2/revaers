import os
import io
import zipfile
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from hornstone.alchemy import Base
from revaers.models import Data
from revaers.parser import parse_csv
from revaers.parser import parse_csvfile


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

csv_dates = [
    (2, 19),
    (2, 26),
    (3, 5),
    (3, 12),
    (3, 19),
    (3, 26),
    (4, 2),
    ]



csv_directory = '/freespace/home/umeboshi/mscourtstuff/covid-19/reports'

s = Session()

def get_csv_files(dates=csv_dates, root=csv_directory):
    for month, day in dates:
        filename = get_zip_file(2021, month, day)
        filename = os.path.join(csv_directory, get_zip_file(2021, month, day))
        # print(filename, os.path.isfile(filename))
        with zipfile.ZipFile(filename) as zfile:
            # breakpoint()
            print(zfile)
            with io.TextIOWrapper(zfile.open('2021VAERSDATA.csv'),
                                  errors='replace') as csvfile:
                parse_csvfile(csvfile, s)
        



def get_death_times(session):
    dead = session.query(Data).filter_by(died=True)
    days = dict()
    for patient in dead:
        if patient.datedied and patient.vax_date:
            days[patient.vaers_id] = patient.datedied - patient.vax_date
    return days

