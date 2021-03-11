from sqlalchemy import (
    Column,
    Integer,
    Unicode,
    Date,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from hornstone.alchemy import Base, SerialBase

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

unused_data_csv_fieldnames = [
    'VAERS_ID', 'RECVDATE', 'STATE', 'AGE_YRS', 'CAGE_YR',
    'CAGE_MO', 'SEX', 'RPT_DATE', 'SYMPTOM_TEXT', 'DIED',
    'DATEDIED', 'L_THREAT', 'ER_VISIT', 'HOSPITAL',
    'HOSPDAYS', 'X_STAY', 'DISABLE', 'RECOVD', 'VAX_DATE',
    'ONSET_DATE', 'NUMDAYS', 'LAB_DATA', 'V_ADMINBY',
    'V_FUNDBY', 'OTHER_MEDS', 'CUR_ILL', 'HISTORY', 'PRIOR_VAX',
    'SPLTTYPE', 'FORM_VERS', 'TODAYS_DATE', 'BIRTH_DEFECT',
    'OFC_VISIT', 'ER_ED_VISIT', 'ALLERGIES'
    ]

class Data(Base, SerialBase):
    __tablename__ = 'vaers_data'
    vaers_id = Column(Integer, primary_key=True)
    recvdate = Column(Date)
    state = Column(Unicode)
    age_yrs = Column(Integer)
    cage_yr = Column(Integer)
    cage_mo = Column(Unicode)
    sex = Column(Unicode)
    rpt_date = Column(Date)
    symptom_text = Column(Unicode)
    died = Column(Boolean)
    datedied = Column(Date)
    l_threat = Column(Unicode)
    er_visit = Column(Unicode)
    hospital = Column(Unicode)
    hospdays = Column(Unicode)
    x_stay = Column(Unicode)
    disable = Column(Unicode)
    vax_date = Column(Date)
    lab_data = Column(Unicode)
    # timespan is diff between datedied and vax_date
    timespan = Column(Integer)
    # True when datedied - vax_date < 0
    bad_dates = Column(Boolean, default=False)
    # True when datedied - vax_date > 360
    questionable = Column(Boolean, default=False)

class MiscData(Base, SerialBase):
    __tablename__ = 'vaers_misc_data'
    vaers_id = Column(Integer, ForeignKey('vaers_data.vaers_id'),
                      primary_key=True)



