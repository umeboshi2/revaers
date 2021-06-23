from sqlalchemy import func, or_
from .models import Data, VaxData


def base_cvquery(session):
    query = session.query(Data, VaxData).join(VaxData)
    query = query.filter(VaxData.vax_type == 'COVID19')
    return query


def cvreports_until(session, end_date):
    return base_cvquery(session).filter(Data.recvdate <= end_date)


def get_vax_manus(session, end_date):
    query = cvreports_until(session, end_date)
    query = query.distinct(VaxData.vax_manu).group_by(VaxData.vax_manu,
                                                      Data.vaers_id,
                                                      VaxData.vaers_id)
    return [r.VaxData.vax_manu for r in query]


def search_symptoms_like(session, text):
    query = base_cvquery(session)
    query = query.filter(Data.symptom_text.ilike('%{}%'.format(text)))
    return query


def csv_update_backlog(session, csvdate):
    query = session.query(func.count(Data.vaers_id).label('events'),
                          func.extract('month', Data.recvdate).label('month'))
    query = query.filter(Data.csvdate == csvdate)
    query = query.group_by(func.extract('month', Data.recvdate))
    query = query.order_by('month')
    return query


def get_csvdates(session):
    query = session.query(Data).distinct(Data.csvdate).order_by(Data.csvdate)
    return [row.csvdate for row in query]
