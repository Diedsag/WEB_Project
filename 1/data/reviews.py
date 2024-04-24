import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Review(SqlAlchemyBase):
    __tablename__ = 'reviews'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')
    tour_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("tours.id"))
    tour = orm.relationship('Tour')
    grade = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    comment = sqlalchemy.Column(sqlalchemy.String, nullable=True)
