from flask import Blueprint, render_template, redirect, url_for, send_from_directory

homeBP = Blueprint("home",__name__)

@homeBP.route("/", methods=["GET"])
def index():
	#print url_for('homeBP.static', filename='layout.html')
	#return render_template("index.html", title="Home")
	return render_template('layout.html')