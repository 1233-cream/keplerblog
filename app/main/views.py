# coding :utf-8
from flask import flash, session, request, render_template, url_for, redirect, abort, current_app
from os import path
from . import main
from .. import db
from ..models import User, Role, Post, Comment, Category
from flask_login import login_required, current_user
from .forms import CommentForm, PostForm


basepath = path.abspath(path.dirname(__file__))
filename = path.join(basepath,'vim_end.md')
#  basepath = path.abspath('.')

@main.route('/', methods=['GET', 'POST'])
@main.route('/index', methods=['GET', 'POST'])
def index():
    posts = Post.query.all()
    PER_POSTS_PER_PAGE=10
    #  做分页 #  从request（/index?page=1)里获取页数1
    #  sqlalchemy的paginate(分页)方法,page_index被初始化为1了
    #  per_page标识每页显示的数量, error_out=False超出页数范围不报错,显示控列表
    page_index = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(
            Post.create_time.desc()).paginate(
                    page_index, per_page = PER_POSTS_PER_PAGE,
                    error_out=False
                    )
    posts=pagination.items

    #  category = Category.query.filter_by(name = 'others').first() # name对应的标签对象
    #  count = db.session.query(Post).filter(Post.category_id == category.id).count()

    categorys = Category.query.order_by(Category.id)[::-1] # 所有标签

    #  category = Category.query.filter_by(name = name).first() # name对应的标签对象
    #  posts = category.posts
    return render_template('index.html', title = 'Kepler',
            posts = posts, categorys = categorys, pagination = pagination)

    #  @app.route('/user/<int: user_id>')
#  @app.route('/user/<regex("[a-z]+"):name>')
@main.route('/user/<name>')
def user(name):
    user = User.query.filter_by(name=name).first()
    if user is None:
        abort(404)
    return render_template('user.html', name=name)




# ------- 帖子 -------

@main.route('/posts/<int:id>', methods = ['GET','POST'])
#  @login_required
def post(id):
    #  detail详情页
    post = Post.query.get_or_404(id)
    form = CommentForm()

    #  保存评论
    if form.validate_on_submit():
        comment = Comment( author_id = current_user.id, body = form.body.data, post = post)
        db.session.add(comment)
        return redirect(url_for('.post', id=post.id, page=-1))

    form.body.data=''
    return render_template('posts/detail.html', title=post.title, form=form, post=post)


@main.route('/edit', methods = ['GET', 'POST'])
@main.route('/edit/<int:id>', methods = ['GET','POST'])
@login_required
def edit(id=0):
    form = PostForm()
    # 新增, current_user当前登录用户
    if id == 0:
        post = Post(author_id = current_user.id)
    else:
        post = Post.query.get_or_404(id)
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.post', id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    post.title = ('添加新文章')
    mode='添加' if id>0 else '编辑'
    return render_template('posts/edit.html', title ='%s - %s' % (mode, post.title), form=form, post=post)


@main.route('/category/<name>', methods=['GET', 'POST'])
def category(name):
    #  点击index的标签后跳到这里,顺便把标签名传了过来,
    #  index视图那里也不需要进行查询,因为做了外键,直接可以有posts知道category
    #  categorys = Category.query.order_by(Category.id)[::-1] # 所有标签
    categorys = Category.query.order_by(Category.id)[::-1] # 所有标签
    category = Category.query.filter_by(name=name).first() # name对应的标签对象
    posts = category.posts

    # TODO  # TODO 标签显示出来的文章怎么分页？？？
    page_index = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.create_time.desc()).paginate( page_index, per_page = 8, error_out=False)


    return render_template("category.html", posts=posts, categorys=categorys, pagination=pagination)


'''
@main.route('/edit-profile', methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('You Profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.date = current_user.name
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form = form)
'''


#  上传文件
@main.route('/upload', methods = ['GET', 'POST'])
def upload():
    if request.method=='POST':
        f = request.files['file']
        basepath = path.abspath(path.dirname(__file__))
        upload_path = path.join(basepath,'static/uploads')
        f.save(upload_path, secure_filename(f.filename))
        return redirect(url_for('main.upload'))
    return render_template('upload.html')


@main.route('/archive')
def archive():
    return render_template('archive.html')


@main.route('/projects/')
def projects():
    return render_template('projects.html')


@main.route('/about')
def about():
    return render_template('about.html')

@main.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

'''

#  定义自己的jinja2过滤器
@app.template_filter('reverse')
def reverse_filter(s):
    return s[::-1]

@app.template_filter('md')
def markdown_to_html(txt):
    from markdown import markdown
    return markdown(txt)

#  -------------
#  通过上下文处理器把方法注册进去,这样所有模板都可以使用这个方法/变量
#  所以就可以将文件读取到变量然后传递到jinja供模板使用,
#  读取md文件并显示到模板中
def read_md(filename):
    with open(filename) as md_file:
        content = reduce(lambda x, y: x + y, md_file.readlines()) #  读取文件,注意reduce要从functools导入
    return content


#  注册方法到程序上下文
@app.context_processor
def inject_methods():
    return dict(read_md=read_md)


@app.template_test('current_link')
def is_current_link(link):
    return link[0] is request.url

'''

#  @app.route('/qsbk')
#  def qsbk():
    #  lines = f.readlines()
    #  return render_template('qsbk.html',lines=lines)

