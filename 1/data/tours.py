import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Tour(SqlAlchemyBase):
    __tablename__ = 'tours'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    first_day = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    last_day = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    people = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    company_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("companies.id"))
    company = orm.relationship('Company')
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    place = sqlalchemy.Column(sqlalchemy.String, nullable=True)
