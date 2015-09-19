from flask import Blueprint, render_template, request, jsonify
from werkzeug import secure_filename
from bigbinf_web.lib.docker_remote import *
from bigbinf_web import config
from bigbinf_web.scheduling import scheduling
import tarfile
import tempfile
from tarfile import TarError
import cStringIO

homeBP = Blueprint('home',__name__)

@homeBP.route('/', methods=['GET'])
def index():
	#print url_for('homeBP.static', filename='layout.html')
	#return render_template('index.html', title='Home')
	return render_template('layout.html')


@homeBP.route('/submitjob', methods=['POST'])
def submit_job():
	file = request.files['file']
	if file:
		try:
			file.filename = secure_filename(file.filename)

			# only except tar files with supported compression
			tar_file = tarfile.open(fileobj=file)
			tar_file.close()
			# tarfile reads some of the file to find the compression
			file.seek(0)
			
			# flask closes its file after the request is complete.
			# create a seperate file which stays open.
			temp = cStringIO.StringIO()
			file.save(temp)
			temp.seek(0)
			file = temp

			scheduling.add_job(file)
			response = jsonify({'status': 'build_queue'})
			
		except TarError as e:
			response = jsonify({'status': 'bad_file', 'supported_filetypes':[{'filetype': 'tar'}, {'filetype': 'tar.gz'}, {'filetype': 'tar.bz2'}]}), 400

		return response