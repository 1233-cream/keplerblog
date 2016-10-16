# coding:utf-8
# import mysql.connector
from . import db, login_manager
from flask.ext.login import UserMixin
from markdown import markdown
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    body = db.Column(db.String(64))
    body_html = db.Column(db.String(64)) #  把markdown原文格式成html存到数据库，而不是访问时在格式
    create_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='post')
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categorys.id'))

    @staticmethod
    def on_body_changed(target, value, oldvalue, initiator):
        target.category= Category.query.filter_by(name='others').first()
        if value is None or (value is ''):
            target.body_html = ''
        else:
            target.body_html= markdown(value)

db.event.listen(Post.body, 'set', Post.on_body_changed)# 当body被修改时触发


class Category(db.Model):
    __tablename__ = 'categorys'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    posts = db.relationship('Post', backref = 'category')

    @staticmethod
    def seed():
        db.session.add_all(map(lambda r:Category(name=r), ['others']))
        db.session.commit()


class Comment(db.Model):
    __tablename__='comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(64))
    create_time= db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))# 表示该列的值是posts表的id


class Role(db.Model):
    __tablename__='roles' # 指定表名
    id = db.Column(db.Integer, primary_key = True) # 定义列对象
    name = db.Column(db.String(20), unique = True)
    users = db.relationship('User', backref = 'role', lazy='dynamic')
    #  users属性添加到Role模型中,用来返回与角色相关联的用户组成的列表,
    #  第一个参数表示这个关系的另一端是哪个模型
    #  backref则表示向User模型添加一个role属性,
    #  从而定义反向关系，这个属性可替代role_id来访问Role表
    #  lazy 指定如何加载相关记录

    @staticmethod
    def seed(): #  调用这个方法就可以设置Role的默认值了
        db.session.add_all(map(lambda r:Role(name=r), ['administrators', 'moderators', 'guests']))
        db.session.commit()


class User(db.Model, UserMixin):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20), nullable = False)
    email=db.Column(db.String(60), nullable = False)
    passwd_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id')) # 表示该列的值是role表的id
    posts = db.relationship('Post', backref='author')
    comments = db.relationship('Comment', backref='author')

    def __str__(self):
        return 'id:{}\tname:{}\temail:{}\tpasswd:{}'.format(self.id, self.name, self.email, self.passwd)

    @staticmethod
    def on_created(target, value, oldvalue, initiator):
        target.role= Role.query.filter_by(name='guests').first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    # user.password=''设置存入生成的散列密码 # user.varify_password(passwd)来校验密码
    @password.setter
    def password(self, passwd):
        self.passwd_hash = generate_password_hash(passwd)

    def verify_password(self, passwd):
        return check_password_hash(self.passwd_hash, passwd)


#用户的回调函数
#  把已经登录的用户id放到session里,告诉flask-login怎么看哪些用户已经登录,
#  然后其他地方需要的时候可以直接通过current_user来获取当前登录用户的信息,如:current_user.name
#  login_manager验证用户登录成功后会派发cookie到浏览器，用户访问另一个页面的时候
#  会读取这个cookie，实际上这个cookie存的就是这个id
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

db.event.listen(User.name, 'set', User.on_created) #  数据库on_created事件监听 #  每插入新对象就初始化用户的Role_id为guests

