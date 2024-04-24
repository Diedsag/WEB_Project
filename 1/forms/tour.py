from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired


class AddTourForm(FlaskForm):
    title = StringField('Название тура', validators=[DataRequired()])
    first_day = DateField('Первый день тура', validators=[DataRequired()])
    last_day = DateField('Второй день тура', validators=[DataRequired()])
    place = StringField('Место тура', validators=[DataRequired()])
    people = SelectMultipleField('Выберите имена людей, бывших в туре', validators=[DataRequired()], choices=[])
    company_name = SelectField('Выберите название компании', validators=[DataRequired()], choices=[])
    submit = SubmitField('Добавить тур')

    def set(self, people, companies):
        self.people.choices = people
        self.company_name.choices = companies
