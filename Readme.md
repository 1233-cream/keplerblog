[TOC]

# 1  结构

## 1.1 run.py
    用于启动一个服务器，它从包获得应用副本并运行，不会在生产环境中用到。

## 1.2 requestments.txt
    用于列出应用所以来的所有python包，分为生产依赖、开发依赖

## 1.3 config.py
    包含应用需要的大多数配置变量

## 1.4 instance/config.py
    数据库配置等东西全放到里面

## 1.5 app/__init__.py
    用于初始化应用并把所有其他的组件组合在一起

## 1.6 app/views.app
    定义了路由

## 1.7 app/models.py
    定义了应用的模型

## 1.8 app/static
    网站静态文件

## 1.9 manage.py
    外部脚本，通过shell来运行,用来测试吧


# 2  csrf
    扩站点请求保护
    避免来自其他地方的post请求,需要标记post请求的来源,以免视图函数也去处理这些请求
    所以，需要识别这些请求是当前服务器输出的ui页面的post请求,进行wsgi配置就行了

# 3  请求上下文
    request: 请求对象，封装在客户端发出的HTTP请求中的内容
    session: 用来保存存储请求之间需要记住的值的字典
    current_app: 当前程序的实例
    g:
    请求钩子?


# 4  WTF
    validate_* 可以自己定义Field 的校验,并且这个会自动被调用来进行校验


# 5  数据库
[ORM框架:SQLAlchemy](http://docs.sqlalchemy.org/en/latest/contents.html)

## 5.1 mysql数据库
    pip install mysql-connector-python-rf
    RUI:mysql+mysqlconnector://username:password@server/db
    不支持中文?

## 5.2 数据库事件
    触发器:操作表的时候触发一些事件
    事件:可以这样啊,每次插入用户都默认初始化他的role_id为guests

## 5.3 Flask-migrate
    需要注意：也要放入版本控制中
    正常操作步骤跟着狗书走就对了
    其实就是一个版本控制的作用,比如需要更新表结构,或者需要迁移到新机器上,
    migrate会自动创建数据迁移脚本
    定义好模型，应该是就可以进行数据库迁移的了，但是我在迁移的过程中，遇到
    几个错误:
    > 1. python manager.py db migrate -m "update"
        python manager.py upgrade 提示我的数据库没有up to date
    > 2. 提示我某张数据表已经存在? why？
    最后我删掉了数据库里的表和migration文件夹，按照狗书重新来了一遍就好了

## 5.4 sqlalchemy增删查改,错误
* sqlalchemy.exc.invalidRequestError这什么鬼错误，到处搜不到[答案](https://segmentfault.com/q/1010000005080603)

## 5.5 密码散列
    werkzeug库的security可以进行散列密码的计算，
    generate_password_hash(passwd, method...)方法计算原始密码的散列值
    check_password_hash(hash,passed)方法检查给出的hash密码与明文密码是否相符
    由于密码是只写的，所以注册的时候怎么写入密码呢?user.passwd=form.passwd.data
    验证登录的时候看一下form.email.data对应的check_password_hash是不是True就可以了

## 5.6 SUMMERY
    主要还是要建好表的映射，当然还有数据库事件触发器、seed、staticmethod这些也要懂


# 6  蓝图
    蓝图就像app里的模块，将不同的功能划分到不同的蓝图里,所以，
    蓝图有自己独立的静态文件独立的views等文件

## 6.1 端点endpoint
    url_for():为了防止后期改动需要频繁更换url所以引入端点,
    如url_for('auth.index', *argv)那么对应的端点就是blueprint.index,

## 6.2 全程
    其实也简单,前面说蓝图就是将不同功能的划分到不同模块中，方便管理而已，
    在没有使用蓝图之前只是采用了工厂方法，将初始化app的部分包装在函数里,
    然后放到__init__.py里，这样app包下导入方便,把处理数据库的models独立出来,
    把配置config独立出来，把视图view独立出来,结构还是挺清晰的，不过随着views
    越写越长，维护起来就不太好了.
         所以换个蓝图来组织代码.
    1. 先按需要组织好文件,放在自定义的文件夹里,就是先把views或form放对位置,
    然后引用蓝图编辑__init__.py 把这个文件夹初始化成一个包
    2. 到app/这个主文件夹下的__init__.py去注册当初定义的蓝图
    3. 最重要的还是引入蓝图后访问的URL由'localhost:5500/about'变为了'/localhost:5500/main/about.html',
       使用了url_for('index')的也需要将改为url_for(main.index)
       弄了好久，一直提示说找不到endpoint，原来是因为我用了nav插件做导航栏，
       但是没将链接改为auth.index


# 7 发送确认邮件
## 7.1 app/email.py
       怎么使用falsk-email来发邮件?配置email.py的时候, 要注意导入上下文?顺便导入配置文件里的变量?

## 7.2 发送确认邮件
       注册函数那里实例化User后,根据用户的id生成token,然后执行email函数发送一个带token的连接给用户,
       用户点击这个确认链接后就会访问到'/confirm/<token>'这个视图,这个视图调用models里的confirm函数对用户进行校验,
       如果校验成功就把confirmed设置为1,我们可以根据这个值判断用户是否点击了确认邮件，
       如果没有点击(confirmed=0)可以限制哪些页面用户可以访问
       template那里的参数,我直接在里面写'/auth/email/'就会自动选取app/template/auth/...下的HTML了;

## 7.3 什么？令牌
    itsdangerous
    注册或找回密码的时候需要发一个确认连接，这个链接肯定是加密的是唯一的，就叫做令牌吧token
    如果点了我发过去的确认邮件，我就讲你的confirmed值设置为True
    token的过程是怎么样的？ 看models里的注释吧，写得挺清楚的

## 7.4 sqlalchemy是自动提交的
    一切就绪了,注册完后也会发送确认邮件了,但是我点击了确认邮件,confirmed字段却没有被设置为1.
    理论上，在config中设置了SQLALCHEMY_COMMIT_ON_TEARDOWN = True的话是会自动提交的,
    也就是只要db.session.add(self)就行,不需要db.session.commit(),结果发现我单词写错了!!!!!!!


# 8 [Flask-Login](http://www.cnblogs.com/agmcs/p/4445428.html)
    还是看官方文档好啊，至少说的明白清楚,搞清楚 继承UserMixin, login_request @login_manager.user_loader回调函数

## 8.1 我的时间?
    moment插件? 注册时间? 怎么实现上次登录时间? 就是登录就显示时间而已。

# 9 帖子和评论
## 9.1 how?
    很简单啦其实，一样，只是数据库操作啊，前面也定义好了表了;
    一个posts和一个edit, template/posts页面

## 9.2 markdown? 左右
    就是那种啊，一边编辑，一般预览啊; 装了markdown插件，我还是不会写页面啊，尴尬，甚至连那些标签都不懂，，，，
    [那怎么做个编辑框啊?](https://segmentfault.com/q/1010000004406545)

## 9.3 怎么在页面显示文章摘要啊？
