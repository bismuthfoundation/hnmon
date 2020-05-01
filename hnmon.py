import re
import requests
import json
import tornado.ioloop
import tornado.web
import time
import threading

class State:
    def update(self):
        try:
            self.link = "https://hypernodes.bismuth.live/status.json"
            self.state_data = json.loads(requests.get(self.link).text)
            self.max_block = (max(self.state_data.values()))
            self.highest_saved = get_id()
        except:
            print("Error fetching data, skipping run")
            pass

def locate(ip_list):
    output_list = []

    for ip in ip_list:

        block = state.state_data.get(ip)
        status = "OK"

        if not block or block == -1:
            block = 0
            status = "Error"

        output_list.append({"ip": ip,
                            "block": block,
                            "tailing": state.max_block - block,
                            "status": status})

    return output_list

def get_next_id():
    with open("sessions.json", "r") as session_file:
        session_dict = json.loads(session_file.read())
        return session_dict["highest"] + 1

def get_id():
    with open("sessions.json", "r") as session_file:
        session_dict = json.loads(session_file.read())
        return session_dict["highest"]

def load_session(number):
    with open("sessions.json", "r") as session_file:
        session_dict = json.loads(session_file.read())
    return session_dict[number]

def save_session(data):
    with open("sessions.json", "r") as session_file:
        session_dict = json.loads(session_file.read())

    id = get_next_id()
    session_dict[id] = data
    session_dict["highest"] = id

    with open("sessions.json", "w") as session_file:
        session_file.write(json.dumps(session_dict))

    return str(id)

class ThreadedClient(threading.Thread):
    def __init__(self, state):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            state.update()
            time.sleep(360)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("monitor.html",
                    state_data=state.state_data)

class SavedHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("saved.html",
                    highest_saved=state.highest_saved)

class HypernodeHandler(tornado.web.RequestHandler):
    def get(self, number):
        data = locate(load_session(number))
        self.render("display.html", data=data)

    def post(self):
        checkboxes = self.get_arguments("checkbox")
        redirect_id = save_session(checkboxes)
        self.redirect("/monitor/"+redirect_id)

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/monitor/(.*)", HypernodeHandler),
        (r"/session_register", HypernodeHandler),
        (r"/saved", SavedHandler),
    ])

if __name__ == "__main__":
    state = State()
    background = ThreadedClient(state)
    background.start()

    app = make_app()
    app.listen(1323)
    tornado.ioloop.IOLoop.current().start()