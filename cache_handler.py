#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    @Author  : minglei.guo
    @Contact : minglei.guo@17zuoye.com

    @Version : 1.0
    
    @File    : cache_handler.py
    @Time    : 2019-09-24
    tornadoredis 模块里的connection 类 实例化iostream时需要把io_loop参数删除。（代码比较旧了）
"""

import functools
import tornado.gen
import tornadoredis
import tornado_mysql
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url


REDIS_CLIENT = tornadoredis.Client(host="127.0.0.1", port=6379)


def redis_cache(func):
    @functools.wraps(func)
    def wapper(*args, **kwargs):
        cache_key = "name2"
        print "wapper 1"
        value = yield tornado.gen.Task(REDIS_CLIENT.get,cache_key)
        print "wapper 2"
        print "result:{}".format(value)
        if not value:
            print "no redis"
            value = func(*args, **kwargs)
            print "func:{}".format(value)
            if value:
                _ = yield tornado.gen.Task(REDIS_CLIENT.set, cache_key, value)
                print _
        else:
            print "get_redis"

        raise tornado.gen.Return(value)
    return wapper


@tornado.gen.coroutine
@redis_cache
def add(a, b):
    result = a + b
    return result


class HelloHandler(RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        result = yield add(1,2)
        if not result:
            result = "1"
        self.write(str(result))
        self.finish()


def make_app():
    return Application([
        url(r"/", HelloHandler),
        ])


def main():
    app = make_app()
    app.listen(8888)
    IOLoop.current().start()


if __name__ == "__main__":

    main()
