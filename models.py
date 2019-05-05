# -*- coding: UTF-8 -*-
from datetime import datetime
from app import db


class HostsModel(db.Model):
    __tablename__ = 'hosts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    domain = db.Column(db.String(64), index=True)
    ip = db.Column(db.String(128))
    note = db.Column(db.String(64))
    status = db.Column(db.SmallInteger, default=0, index=True)  # 0: 激活, 1: 禁用
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    status_mapping = {
        -1: '删除',
        0: '启用',
        1: '禁用',
    }

    # 声明排序方式
    __mapper_args__ = {
        "order_by": last_seen.desc()
    }


    @staticmethod
    def add_host(attr_dict, *args, **kwargs):
        """
        添加本地用户
        """
        host = HostsModel(
            domain=attr_dict["domain"],
            ip=attr_dict["ip"],
            status=attr_dict["status"],
            note=attr_dict["note"],
        )
        db.session.add(host)
        db.session.commit()
        return host

    @staticmethod
    def list(page=0, per_page=10, kw=None):
        """
        获取分页列表
        :param page:  第几页
        :param per_page:　每页多个数据
        """
        query = HostsModel.query.filter(HostsModel.status.notin_([-1]))
        if kw:
            query = query.filter(HostsModel.domain.like('%{}%'.format(kw)))
        pagination = query.paginate(page, per_page=per_page, error_out=False)
        data = [p.to_json() for p in pagination.items]
        return data, pagination.total

    @staticmethod
    def item(id=None):
        """
        获取单条记录
        """
        data = HostsModel.query.filter_by(id=id).first()
        return data.to_json() if data else []

    def to_json(self):
        item = {
            "id": self.id,
            "domain": self.domain,
            "ip": self.ip,
            "note": self.note,
            "status": self.status_mapping[self.status],
            "status_id": self.status,
            "last_seen": self.last_seen.strftime("%Y-%m-%d %H:%M:%S")
        }
        return item

    def update(self, data_dict):
        self.ip = data_dict['ip']
        self.note = data_dict['note']
        self.status = data_dict['status']
        db.session.commit()
        return self.to_json()

    def delete(self):
        self.status = -1
        db.session.commit()

