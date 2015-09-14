from flask import Blueprint, render_template, request, jsonify, abort, Response, stream_with_context
from werkzeug import secure_filename
from bigbinf_web.lib.docker_remote import *
from bigbinf_web import config
from uuid import uuid4
import json

homeBP = Blueprint('home',__name__)

@homeBP.route('/', methods=['GET'])
def index():
	#print url_for('homeBP.static', filename='layout.html')
	#return render_template('index.html', title='Home')
	return render_template('layout.html')


@homeBP.route('/submitjob', methods=['POST'])
def submitJob():
	file = request.files['file']
	if file:
		filename = secure_filename(file.filename)
		imagename = str(uuid4())
		builder_url = '%s:%s' % (config.builder_host, config.builder_port)
		registry_url = '%s:%s' % (config.registry_host, config.registry_port)

		def job_generator():
			response = remote_build(file, builder_url, registry_url, imagename)
			for line in response:
				build_status = line
				yield build_status

			build_success_str = 'Successfully built'
			if not build_success_str in build_status:
				abort(400)

			response = remote_push_registry(builder_url, registry_url, imagename)
			response = list(response)
			push_success_str = 'Image successfully pushed'
			if not push_success_str in response[-2]:
				abort(400)
			#jsonify doesn't work with streaming for some reason
			yield json.dumps({'stream': 'Successfully pushed image to private repository'})
	return Response(stream_with_context(job_generator()), mimetype='application/json')
