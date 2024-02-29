from flask import Flask, render_template, redirect
from flask_dance.contrib.github import make_github_blueprint, github
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_socketio import SocketIO
from random import randint
from time import sleep
import threading
import os


os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
blueprint = make_github_blueprint(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
)
app.register_blueprint(blueprint, url_prefix="/login")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
socketio = SocketIO(app)


result = 0


@app.route('/')
@app.route('/home')
def index():
    if not github.authorized:
        return render_template("unauthorised.html")
    resp = github.get("/user")
    assert resp.ok
    return redirect('/generator')


is_randomize = False


@app.route('/generator', methods=['GET'])
def generator():
    if not github.authorized:
        return redirect('/')
    if not is_randomize:
        thread_rand = threading.Thread(target=random_number)
        thread_rand.start()
    return render_template("index.html", result=result, login=github.get("/user").json()["login"])


@app.route("/logout")
def logout():
    del blueprint.token
    return redirect('/')


def random_number():
    global is_randomize
    is_randomize = True
    while True:
        global result
        result = randint(0,100)
        print(result)
        socketio.emit('response', result)
        sleep(5)


if __name__ == '__main__':
    app.run()
