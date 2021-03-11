import csv
from datetime import datetime
from .models import Data


def get_zip_file(year):
    filename = "{}VAERSData.zip".format(year)
    return filename


date_fields = [
    'recvdate',
    'rpt_date',
    'datedied',
    'vax_date',
    ]

text_fields = [
    'state',
    'cage_mo',
    'sex',
    'symptom_text',
    'l_threat',
    'er_visit',
    'hospital',
    'hospdays',
    'x_stay',
    'disable',
    'lab_data',
    ]

int_fields = [
    'age_yrs',
    'cage_yr',
    ]


def make_row_data(row):
    data = Data()
    data.vaers_id = int(row['VAERS_ID'])
    for field in text_fields:
        text = row[field.upper()].strip()
        setattr(data, field, text)
    for field in int_fields:
        text = row[field.upper()].strip()
        if text:
            setattr(data, field, int(float(text)))
    for field in date_fields:
        text = row[field.upper()].strip()
        if text:
            value = datetime.strptime(text, '%m/%d/%Y').date()
            setattr(data, field, value)
    data.died = False
    died = row['DIED'].strip()
    if died and died == 'Y':
        data.died = True
        #  raise RuntimeError("bad died {}".format(died))
        if data.datedied and data.vax_date:
            timespan = data.datedied - data.vax_date
            if timespan.days >= 0 and timespan.days < 360:
                data.timespan = timespan.days
            if timespan.days < 0:
                data.bad_dates = True
            if timespan.days > 360:
                data.questionable = True
    return data

def parse_csvfile(csvfile, session):
    reader = csv.DictReader(csvfile)
    rows = list()
    for row in reader:
        vaers_id = int(row['VAERS_ID'])
        data = session.query(Data).get(vaers_id)
        if data is None:
            data = make_row_data(row)
            session.add(data)
            session.commit()

        if row['DATEDIED']:
            print(row['DATEDIED'], row['VAX_DATE'])
            rows.append(row)
    


def parse_csv(filename, session):
    with open(filename, 'r', errors='replace') as csvfile:
        parse_csvfile(csvfile, session)
