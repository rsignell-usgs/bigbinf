from flask import Flask

app = Flask(__name__)

from bigbinf_web.controllers import homeBP


app.register_blueprint(homeBP)


