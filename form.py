# -*- coding: utf-8 -*-

try:
    from flask_wtf import FlaskForm  # Try Flask-WTF v0.13+
except ImportError:
    from flask_wtf import Form as FlaskForm  # Fallback to Flask-WTF v0.12 or older
from models import HostsModel
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, ValidationError, Length, Email
import utils


class AddHostForm(FlaskForm):
    domain = StringField('domain', [])
    ip = StringField('ip', [])
    note = StringField('note', [])
    status = StringField('status', [])

    def validate_domain(self, field):
        query = HostsModel.query.filter(HostsModel.status.notin_([-1]))
        if query.filter_by(domain=field.data).count() > 0:
            raise ValidationError('domain already exists.')

    def validate_ip(self, field):
        if utils.is_valid_address(field.data) is False:
            raise ValidationError("ip address is incorrect")


class EditHostForm(FlaskForm):
    domain = StringField('domain', [])
    ip = StringField('ip', [])
    note = StringField('note', [])
    status = StringField('status', [])

    def validate_ip(self, field):
        if utils.is_valid_address(field.data) is False:
            raise ValidationError("ip address is incorrect")


# 用户登录验证表单
class LoginUserForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(message='用户名不能为空')])
    password = PasswordField('password', validators=[DataRequired(message='密码不能为空')])
