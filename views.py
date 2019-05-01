from flask import Blueprint, render_template, redirect, jsonify, request
from models import HostsModel
from form import AddHostForm, EditHostForm

mod = Blueprint('general', __name__)


@mod.route('/api/hosts', methods=['GET', 'POST'])
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
            HostsModel.add_host(form.data)
            return jsonify({"code": 0, "msg": "success"})
        return jsonify({
            "code": 1,
            "msg": form.errors[form.errors.keys()[0]]
        })


@mod.route('/api/hosts/<int:id>', methods=['PUT', 'DELETE'])
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


@mod.route('/')
def index():
    return render_template('index.html')


@mod.route('/service')
def service():
    return render_template('service.html')


@mod.route('/favicon.ico')
def favicon():
    return redirect("http://static.g.iqiyi.com/pcw/favicon32.ico")


@mod.errorhandler(404)
def not_found():
    return "404", 404







