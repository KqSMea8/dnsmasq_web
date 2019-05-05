# -*- coding: utf-8 -*-

import os
import sys
try:
    reload(sys)
    sys.setdefaultencoding("utf-8")
except:
    pass

from flask import Blueprint, render_template, redirect, jsonify, request, url_for
from models import HostsModel, UserModel
from form import AddHostForm, EditHostForm, LoginUserForm
from flask_login import login_user, logout_user, current_user, login_required, login_manager
import utils

mod = Blueprint('general', __name__)


@mod.route('/')
@login_required
def index():
    return render_template('index.html')


@mod.route('/login')
def login():
    return render_template('login.html')


@mod.route('/favicon.ico')
def favicon():
    return redirect("http://static.g.iqiyi.com/pcw/favicon32.ico")


@mod.errorhandler(404)
def not_found():
    return "404", 404


@mod.route('/api/hosts', methods=['GET', 'POST'])
@login_required
def hosts():
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        kw = request.values.get('kw', '')
        (data, total) = HostsModel.list(page=page, per_page=per_page, kw=kw)
        page_data = {
            "limit": per_page,
            "page": page,
            "data": data,
            "total": total,
            "code": 0,
            "message": ""
        }
        return jsonify(page_data)

    if request.method == 'POST':
        form = AddHostForm(csrf_enabled=False)
        if form.validate_on_submit():
            data_dict = form.data
            data_dict.update({"user_id": current_user.id})
            print(data_dict, type(data_dict))
            HostsModel.add_host(data_dict)
            return jsonify({"code": 0, "msg": "success"})
        return jsonify({
            "code": 1,
            "msg": form.errors[form.errors.keys()[0]]
        })


@mod.route('/api/hosts/<int:id>', methods=['PUT', 'DELETE'])
@login_required
def host(id):
    if request.method == 'PUT':
        form = EditHostForm(csrf_enabled=False)
        if form.validate_on_submit():
            host = HostsModel.query.filter_by(id=id).first()
            if host:
                host.update(form.data)
                return jsonify({"code": 0, "msg": "success"})
            return jsonify({"code": 1, "msg": ""})
        return jsonify({
            "code": 1,
            "msg": form.errors[form.errors.keys()[0]]
        })
    if request.method == 'DELETE':
        host = HostsModel.query.filter_by(id=id).first()
        if host:
            host.delete()
            return jsonify({"code": 0, "msg": "success"})
        return jsonify({"code": 1, "msg": ""})


# 批量导入
@mod.route('/api/batch_hosts', methods=['POST'])
@login_required
def batch_hosts():
    data_text = request.form["text"].strip()
    for num, line in enumerate(data_text.split('\n')):
        line_split = line.split()
        if len(line_split) < 2:
            return jsonify({"code": 1, "msg": "%d line, field numbers < 2" % (num + 1)})
        if utils.is_valid_address(line_split[1]) is False:
            return jsonify({"code": 1, "msg": "%d line, ip address is incorrect" % (num + 1)})

    for line in data_text.split('\n'):
        line_split = line.split()
        # 已存在的域名忽略导入
        query = HostsModel.query.filter(HostsModel.status.notin_([-1]))
        if query.filter_by(domain=line_split[0]).count() > 0:
            continue
        data = {
            "domain": line_split[0],
            "ip": line_split[1],
            "status": 0,
            "user_id": current_user.id,
        }
        if len(line_split) < 3:
            data.update({"note": ""})
        else:
            data.update({"note": line_split[2]})
        HostsModel.add_host(data)
    return jsonify({"code": 0, "msg": "success"})


# 生成hosts文件
@mod.route('/gen/hosts/', methods=['GET'])
@login_required
def gen_hosts():
    query = HostsModel.query.filter(HostsModel.status.notin_([-1, 1])).all()
    basedir = os.path.abspath(os.path.dirname(__file__))
    hosts_file = os.path.join(basedir, "hosts.conf")
    with open(hosts_file, 'w') as f:
        for host in query:
            line = "    ".join([
                host.ip,
                host.domain,
                "#" + host.user_rs.name + " " + host.note + " " + host.mtime.strftime("%Y-%m-%d %H:%M:%S") + "\n"
            ])
            f.write(line)
    return jsonify({"code": 0, "msg": ""})


@mod.route('/api/login', methods=['POST'])
def api_login():
    """
    user login
    """
    form = LoginUserForm(csrf_enabled=False)
    user = UserModel.query.filter_by(username=form.username.data).first()
    if form.validate_on_submit():  # 表单验证
        # Login and validate the user.
        ldap_auth_result = UserModel.ldap_validate(form.username.data, form.password.data)  # ldap验证 return: []
        if ldap_auth_result[0]:  # ldap验证
            if not user:
                user = UserModel.add_ldap_user(ldap_auth_result[1])
            user.ping()
            login_user(user)
        else:
            return jsonify({"code": 1, "msg": "账号或者密码错误"})
        return jsonify({"code": 0, "msg": "登录成功"})
    return jsonify({
        "code": 1,
        "msg": form.errors[form.errors.keys()[0]]
    })


@mod.route('/api/logout', methods=['GET', 'POST'])
@login_required
def api_logout():
    logout_user()
    return jsonify({"code": 0, "msg": "注销成功"})


