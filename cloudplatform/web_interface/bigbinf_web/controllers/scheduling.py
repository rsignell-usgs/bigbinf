from flask import Blueprint, request, jsonify
from bigbinf_web.scheduling import scheduling


schedulingBP = Blueprint('scheduling', __name__)


@schedulingBP.route('/queue', methods=['GET'])
def get_schedule():
	return jsonify({'queue': scheduling.get_schedule()})