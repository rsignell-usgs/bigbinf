from flask import Flask, jsonify
from cloud_config import config
app = Flask(__name__)

@app.route("/getclouds")
def get_clouds():
    return jsonify(config)

if __name__ == "__main__":
    app.run(port=5004)
