#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    @Author  : minglei.guo
    @Version : 1.0
    @File    : handler.py
    @Time    : 2019-09-24
"""
import functools
import tornado.web
import tornado.wsgi
import tornado.ioloop
import tornado.options
import tornado.httpserver
from tornado import gen
from tornado.options import define, options
from tornado.websocket import WebSocketHandler
from tornado.httpclient import AsyncHTTPClient, HTTPRequest

define("port", default="9000", help="default port", type=int)


class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("hello,world")


class FileHandler(tornado.web.RequestHandler):
    def post(self):
        data = self.request.body
        f = open("/home/dell/log/9000_1.log", "wb")
        f.write(data)
        f.close()

        # self.write("ok")


class AsyGetDasHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        request = HTTPRequest(url="http://10.100.14.78/client/lastestver",
                              headers={"username": "guominglei"},
                              method="GET",
                              # body="day:20150112;"
                              )

        http_client = AsyncHTTPClient()

        response = yield http_client.fetch(request)  # HttpResponse 实例

        print response
        # logging.debug(response)
        ver_str = response.body

        self.write(ver_str)

        # response1, response2 = yield [http_client.fetch(""),
        #                               http_client.fetch("")]
        # response_dict = yield dict(response3=http_client.fetch(""),
        #                            response4=http_client.fetch(""))
        # response3 = response_dict['response3']
        # response4 = response_dict['response4']


class AsyGetDasTwoHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        result = yield self.fetch_json("http://10.100.14.78/client/lastestver")

        # print result

        self.write(result)

    def fetch_json(self, url):
        response = yield AsyncHTTPClient().fetch(url)
        print "response:{}".format(response.body)
        raise gen.Return(response.body)


class TcpHandler(WebSocketHandler):
    def check_origin(self, origin):
        print origin
        return True

    def open(self):
        print "open"

    def on_message(self, message):
        print "message:{}".format(message)
        self.write("sss")

    def on_close(self):
        print "close"


def main():
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r"/", HomeHandler),
            (r"/data", FileHandler),
            (r"/dasdata2", AsyGetDasTwoHandler),
            (r"/dasdata", AsyGetDasHandler),
            ("r/socket", TcpHandler),  # tcp test
        ], debug=True)

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    #http_server.start(0) # 默认是1如果不等于1 根据CPU数量启动
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
