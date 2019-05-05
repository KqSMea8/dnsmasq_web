# -*- coding: UTF-8 -*-
import datetime
from app import app, db, login_manager
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from ldap3 import Connection, SUBTREE, ServerPool, Server


@login_manager.user_loader
def load_user(id):
    return UserModel.query.get(int(id))


class HostsModel(db.Model):
    __tablename__ = 'hosts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 域名
    domain = db.Column(db.String(64), index=True)
    # ip
    ip = db.Column(db.String(128))
    # 备注
    note = db.Column(db.String(64))
    # 状态
    status = db.Column(db.SmallInteger, default=0, index=True)  # 0: 激活, 1: 禁用
    # 修改用户/创建用户ID
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # 修改用户/创建用户
    user_rs = db.relationship('UserModel', foreign_keys=user_id, backref='HostsModel')
    # 创建时间
    ctime = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
    # 修改时间
    mtime = db.Column(db.DateTime(timezone=True), default=datetime.datetime.now, onupdate=datetime.datetime.now)

    status_mapping = {
        -1: '删除',
        0: '启用',
        1: '禁用',
    }

    # 声明排序方式
    __mapper_args__ = {
        "order_by": mtime.desc()
    }

    @staticmethod
    def add_host(attr_dict, *args, **kwargs):
        """
        添加域名
        """
        host = HostsModel(
            domain=attr_dict["domain"],
            ip=attr_dict["ip"],
            status=attr_dict["status"],
            note=attr_dict["note"],
            user_id=attr_dict["user_id"],
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
            "mtime": self.mtime.strftime("%Y-%m-%d %H:%M:%S"),
            "ctime": self.ctime.strftime("%Y-%m-%d %H:%M:%S"),
            "user": self.user_rs.name
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


class UserModel(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), index=True, unique=True)
    hash_password = db.Column(db.String(128))
    name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(64), index=True, unique=True)
    department = db.Column(db.String(64), index=True)
    source = db.Column(db.String(10), index=True)  # ldap or local
    status = db.Column(db.SmallInteger, default=0, index=True)  # 0: 激活, 1: 禁用
    ctime = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
    last_seen = db.Column(db.DateTime(), default=datetime.datetime.now)

    status_mapping = {
        -1: '删除',
        0: '激活',
        1: '禁用',
    }

    def __repr__(self):
        return '<User %r>' % self.username

    @staticmethod
    def ldap_validate(username, password):
        """
        实现LDAP用户登录验证
        """
        ldap_host = app.config['LDAP_HOST']
        ldap_port = app.config['LDAP_PORT']
        manager_dn = app.config['MANAGER_DN']
        manager_password = app.config['MANAGER_PASSWORD']
        search_base = app.config['SEARCH_BASE']
        ldap_server = Server(ldap_host, port=int(ldap_port))
        ldap_server_pool = ServerPool([ldap_server, ])
        conn = Connection(ldap_server_pool,
                          user=manager_dn,
                          password=manager_password,
                          check_names=True,
                          lazy=False,
                          raise_exceptions=False,
                          receive_timeout=3)
        conn.open()
        conn.bind()
        res = conn.search(
            search_base=search_base,
            search_filter='(sAMAccountName={})'.format(username),
            search_scope=SUBTREE,
            attributes=['cn', 'mail', 'sAMAccountName', 'department', 'manager'],  # ALL_ATTRIBUTES,获取所有属性值
            paged_size=5
        )
        if res:
            entry = conn.response[0]
            dn = entry['dn']
            attr_dict = entry['attributes']
            try:
                # check password by dn
                conn2 = Connection(ldap_server_pool, user=dn, password=password, check_names=True, lazy=False,
                                   raise_exceptions=False)
                conn2.bind()
                if conn2.result["description"] == "success":
                    return True, attr_dict
                else:
                    return False, attr_dict
            except Exception:
                return False, attr_dict
        else:
            app.logger.error("LDAP Error! user attributes is None.")
            return False, None

    # 下面这4个方法是flask_login需要的4个验证方式
    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True

    def is_active(self):
        """True, as all users are active."""
        return True

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    def get_id(self):
        return self.id

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.hash_password = generate_password_hash(password)

    def confirm_password(self, password):
        return check_password_hash(self.hash_password, password)

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def ping(self):
        self.last_seen = datetime.datetime.utcnow()
        db.session.add(self)

    @staticmethod
    def add_ldap_user(attr_dict, *args, **kwargs):
        """
        添加LDAP用户
        """
        user = UserModel(
            username=attr_dict["sAMAccountName"],
            email=attr_dict["mail"],
            name=attr_dict["cn"],
            department=attr_dict["department"],
            hash_password=generate_password_hash(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            source="LDAP"
        )
        db.session.add(user)
        db.session.commit()
        return user


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
            return False

    def ping(self):
        pass


login_manager.anonymous_user = AnonymousUser


