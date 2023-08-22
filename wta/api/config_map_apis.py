from flask import request, make_response
from flask_restful import reqparse
from flask_api import status
from miniagent import api
from miniagent.executer import ExecuterCaller
from miniagent.event_receiver import Resource

class ConfigMap(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('config_map', type=dict)

    def post(self):

        args = ConfigMap.parser.parse_args()

        data = dict(
            initial_param = args['config_map'],
            executer = 'wta.executer.config_map.ConfigMap',
        )

        rtn, rtn_message = ExecuterCaller.instance().execute_command(data)

        if rtn:
            status_code = status.HTTP_200_OK            
        else:
            status_code = status.HTTP_400_BAD_REQUEST

        return rtn_message, status_code

    def get(self):

        data = dict(
            initial_param = {},
            executer = 'wta.executer.config_map.ConfigMap',
        )

        rtn, rtn_message = ExecuterCaller.instance().execute_command(data)

        if rtn > 0:
            status_code = status.HTTP_200_OK
        elif rtn == 0:
            return rtn_message, status.HTTP_204_NO_CONTENT
        else:
            status_code = status.HTTP_400_BAD_REQUEST

        return rtn_message, status_code

    post.permitted_roles = ["config_map"]
    get.permitted_roles = ["config_map"]

api.add_resource(ConfigMap, '/config_map', endpoint='config_map')
