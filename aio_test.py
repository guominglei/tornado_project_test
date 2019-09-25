# -*- coding:utf-8 -*-
"""
    同步工作，异步化例子
    利用后台线程池
"""
import time
import logging
import tornado.web
import tornado.escape
from tornado import gen
import concurrent.futures
import tornado.httpserver
import tornado.httpclient
from tornado.options import define, options
from tornado.concurrent import run_on_executor

executor = concurrent.futures.ThreadPoolExecutor(20)
define("port", default=8888, help="run on the given port", type=int)


class ExpHandler(tornado.web.RequestHandler):
    _thread_pool = executor

    @gen.coroutine
    def get(self, num):
        i = int(num)
        result = yield self.exp(2, i)
        self.write(str(result))
        self.finish()

    @run_on_executor(executor="_thread_pool")
    def exp(self, x, y):
        logging.debug("thread_pool")
        result = x ** y
        return result


class NonblockingHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self, num):
        http_client = tornado.httpclient.AsyncHTTPClient()
        try:
            response = yield http_client.fetch("https://www.baidu.com")
            self.write(response.body)
        except tornado.httpclient.HTTPError as e:
            self.write(("Error: " + str(e)))
        finally:
            http_client.close()
        self.finish()


class SleepHandler(tornado.web.RequestHandler):
    _thread_pool = executor

    @gen.coroutine
    def get(self, sec):
        sec = float(sec)
        start = time.time()
        res = yield self.sleep(sec)
        self.write("Sleeped for {} s".format((time.time() - start)))
        self.finish()

    @run_on_executor(executor="_thread_pool")
    def sleep(self, sec):
        time.sleep(sec)
        return sec


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/exp/(?P<num>[^\/]+)?', ExpHandler),
            (r'/nonblocking/(?P<num>[^\/]+)?', NonblockingHandler),
            (r'/sleep/(?P<sec>[^\/]+)?', SleepHandler)
        ]
        settings = dict(
            debug=True,
            logging="debug"
        )
        tornado.web.Application.__init__(self, handlers, **settings)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    io_loop = tornado.ioloop.IOLoop.instance()
    io_loop.start()


if __name__ == "__main__":
    main()
