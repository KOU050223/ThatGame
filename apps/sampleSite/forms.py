# form情報を定義する
from flask_wtf import FlaskForm
from wtforms import StringField,IntegerField,DateTimeLocalField,PasswordField

class KweetForm(FlaskForm):
    message = StringField()

class ReserveForm(FlaskForm):
    name = StringField()
    startAt = DateTimeLocalField(format='%Y-%m-%dT%H:%M')
    endAt = DateTimeLocalField(format='%Y-%m-%dT%H:%M')
    count = IntegerField()