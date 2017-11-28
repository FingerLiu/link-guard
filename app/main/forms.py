from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, SubmitField
from flask_wtf_storage import MultipleFileField, FileField, StorageForm


class NotifyForm(FlaskForm):
    user_id = StringField()
    payload = StringField()


class RegisterTokenForm(FlaskForm):
    token = HiddenField()


class TestMultiFileFieldForm(StorageForm):
    name = StringField()
    file1 = FileField()
    files1 = MultipleFileField()
    files2 = MultipleFileField()
    submit = SubmitField('確 認')
