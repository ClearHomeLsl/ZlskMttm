# Mysql配置
# docker创建数据库命令
"""
docker pull mysql:8.0.39
docker run --name weilsl_mysql -e MYSQL_ROOT_PASSWORD=WEIlsl0729.# -e MYSQL_DATABASE=HomeClear -e MYSQL_USER=wei -e MYSQL_PASSWORD=WEIlsl0729.# -p 3306:3306 -d mysql:8.0.39
"""
# MacOS通过navicat访问，需要修改密码验证格式(root用户进入mysql)
"""
ALTER USER 'root'@'%' IDENTIFIED WITH 'mysql_native_password' BY 'WEIlsl0729.#';
FLUSH PRIVILEGES;
"""

"""
CREATE USER 'prod'@'%' IDENTIFIED WITH mysql_native_password BY 'WEIlsl0729.#';
GRANT ALL PRIVILEGES ON *.* TO 'prod'@'%' WITH GRANT OPTION;

"""
import environ

env = environ.Env()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env.str('MYSQL_NAME', default='MttmData'),
        'USER': env.str('MYSQL_USER', default='MttmUser'),
        'PASSWORD': env.str('MYSQL_PASSWORD', default='Qiuqi001201.'),
        'HOST': env.str('MYSQL_HOST', default='localhost'),
        'PORT': int(env.str('MYSQL_PORT', default='3306')),
        'CONN_MAX_AGE': 60 * 3,  # 连接最大存活时间(秒)
        'POOL_SIZE': 10,  # 连接池大小
    }
}

