from flask import Blueprint, render_template, request, jsonify, send_from_directory
from werkzeug import secure_filename
from bigbinf_web.lib.docker_remote import *
from bigbinf_web.lib.discovery_service import *
from bigbinf_web.config import config
from bigbinf_web.scheduling import scheduling
import tarfile
import tempfile
from tarfile import TarError
import cStringIO
import os

homeBP = Blueprint('home',__name__)

@homeBP.route('/', methods=['GET'])
def index():
	#print url_for('homeBP.static', filename='layout.html')
	#return render_template('index.html', title='Home')
	return render_template('layout.html')


@homeBP.route('/submitjob', methods=['POST'])
def submit_job():
	file = request.files['file']
	resultspath = request.form.get('resultspath', None)
	datapath = request.form.get('datapath', None)
	if resultspath is not None and not os.path.isabs(resultspath):
		resultspath = None
	if datapath is not None and not os.path.isabs(datapath):
		datapath = None
	print 'paths:', resultspath, datapath
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

			scheduling.add_job(file, datapath, resultspath)
			response = jsonify({'status': 'build_queue'})
			
		except TarError as e:
			response = jsonify({'status': 'bad_file', 'supported_filetypes':[{'filetype': 'tar'}, {'filetype': 'tar.gz'}, {'filetype': 'tar.bz2'}]}), 400

		return response


@homeBP.route('/queue', methods=['GET'])
def get_schedule():
	return jsonify({'jobs': scheduling.get_schedule()})


@homeBP.route('/region', methods=['GET'])
def get_region():
	return jsonify({'region': config.region})


@homeBP.route('/regions', methods=['GET'])
def get_regions():
	hostUrl = 'http://%s:%s' % (config.discovery_service_host, config.discovery_service_port)
	return get_clouds(hostUrl)


@homeBP.route('/deletejob', methods=['DELETE'])
def delete_job():
	print 'delete job'
	job_name = request.args.get('jobname', None)
	if job_name:
		scheduling.delete_job(job_name)
		response = jsonify({'status': 'success'}), 200
	else:
		response = jsonify({'status': 'failed'}), 400
	return response


@homeBP.route('/results', methods=['GET'])
def get_results():
	job_name = request.args.get('jobname', None)
	if job_name:
		job_name = secure_filename(job_name)
		filename = '%s.tar.gz' % job_name
		results_hostpath = os.path.join(config.results_hostpath, filename)

		return send_from_directory(directory=config.results_hostpath, filename=filename)
	else:
		return jsonify({'status': 'failed'}), 400
