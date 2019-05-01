import socket
import re
try:
    from flask_wtf import FlaskForm  # Try Flask-WTF v0.13+
except ImportError:
    from flask_wtf import Form as FlaskForm  # Fallback to Flask-WTF v0.12 or older
from models import HostsModel
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, ValidationError, Length, Email


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
        try:
            socket.inet_pton(socket.AF_INET, field.data)
        except socket.error:  # not a valid address
            try:
                socket.inet_pton(socket.AF_INET6, field.data)
            except socket.error:  # not a valid address
                raise ValidationError("ip address is incorrect")


class EditHostForm(FlaskForm):
    domain = StringField('domain', [])
    ip = StringField('ip', [])
    note = StringField('note', [])
    status = StringField('status', [])

    def validate_ip(self, field):
        try:
            socket.inet_pton(socket.AF_INET, field.data)
        except socket.error:  # not a valid address
            try:
                socket.inet_pton(socket.AF_INET6, field.data)
            except socket.error:  # not a valid address
                raise ValidationError("ip address is incorrect")

