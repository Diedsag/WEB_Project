from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class AddReviewForm(FlaskForm):
    tour_name = StringField('Название тура', validators=[DataRequired()])
    grade = SelectField('Оценка', validators=[DataRequired()], choices=list(map(int, range(11))))
    comment = StringField('Коментарий', validators=[DataRequired()])
    submit = SubmitField('Добавить отзыв')
