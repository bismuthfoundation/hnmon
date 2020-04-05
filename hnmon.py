import re
import requests
import json
import tornado.ioloop
import tornado.web
import time
import threading

class Api:
    def update(self):
        self.link = "https://hypernodes.bismuth.live/status.json"
        self.api_data = json.loads(requests.get(self.link).text)
        self.max_block = (max(self.api_data.values()))

def locate(ip_list):
    output_list = []

    for ip in ip_list:

        block = api.api_data.get(ip)
        status = "OK"

        if not block or block == -1:
            block = 0
            status = "Error"

        output_list.append({"ip": ip,
                            "block": block,
                            "tailing": api.max_block - block,
                            "status": status})

    return output_list

def get_next_id():
    with open("sessions.json", "r") as session_file:
        session_dict = json.loads(session_file.read())
        return int(max(session_dict.keys())) + 1

def load_session(number):
    with open("sessions.json", "r") as session_file:
        session_dict = json.loads(session_file.read())
    return session_dict[number]

def save_session(data):
    with open("sessions.json", "r") as session_file:
        session_dict = json.loads(session_file.read())

    id = get_next_id()
    session_dict[id] = data

    with open("sessions.json", "w") as session_file:
        session_file.write(json.dumps(session_dict))

    return str(id)

class ThreadedClient(threading.Thread):
    def __init__(self, api):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            api.update()
            time.sleep(360)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("menu.html", api_data=api.api_data)

class HypernodeHandler(tornado.web.RequestHandler):
    def get(self, number):
        data = locate(load_session(number))
        self.render("select.html", data=data)

    def post(self, arguments):
        checkboxes = self.get_arguments("checkbox")
        redirect_id = save_session(checkboxes)
        self.redirect(redirect_id)

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/(.*)", HypernodeHandler),
        (r"/session_register", HypernodeHandler),
    ])

if __name__ == "__main__":
    api = Api()
    background = ThreadedClient(api)
    background.start()

    app = make_app()
    app.listen(1323)
    tornado.ioloop.IOLoop.current().start()