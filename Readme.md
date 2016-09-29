1. run.py
用于启动一个服务器，它从包获得应用副本并运行，不会在生产环境中用到。

2. requestments.txt
用于列出应用所以来的所有python包，分为生产依赖、开发依赖

3. config.py
包含应用需要的大多数配置变量

4. instance/config.py

5. app/__init__.py
用于初始化应用并把所有其他的组件组合在一起

6. app/views.app
定义了路由

7. app/models.py
定义了应用的模型

8. app/static
网站文件

9. csrf扩站点请求保护
避免来自其他地方的post请求,需要标记post请求的来源,以免视图函数也去处理这些请求
所以，需要识别这些请求是当前服务器输出的ui页面的post请求,进行wsgi配置就行了

