from flask import Flask
from bigbinf_web.scheduling.job import ExtendedJsonEncoder

app = Flask(__name__)
app.json_encoder = ExtendedJsonEncoder

from bigbinf_web.controllers import homeBP



app.register_blueprint(homeBP)



