from flask import request, make_response
from flask_restful import reqparse
from flask_api import status
from miniagent import api, configure
from miniagent.executer import ExecuterCaller
from miniagent.event_receiver import Resource

class Launcher(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('service', type=str)
    parser.add_argument('env_params', type=dict)

    def post(self):

        args = Launcher.parser.parse_args()

        executer_map = {
            'linuxshell_agent':'linuxshell_agent.LaunchService',
            'k8s_agent':'k8s_agent.LaunchService',
            'docker_agent':'docker_agent.LaunchService',
        }

        data = dict(
            initial_param = args, # two items : service , env_params
            executer = 'wta.executer.'+executer_map[configure['AGENT_NAME']],
        )

        print("## Launcher data : ", data)
        rtn, rtn_message = ExecuterCaller.instance().execute_command(data)

        if rtn:
            status_code = status.HTTP_200_OK            
        else:
            status_code = status.HTTP_400_BAD_REQUEST

        return rtn_message, status_code

    post.permitted_roles = ["launcher"]

class Killer(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('service', type=str)

    def post(self):

        args = Launcher.parser.parse_args()

        executer_map = {
            'linuxshell_agent':'linuxshell_agent.KillService',
            'k8s_agent':'k8s_agent.KillService',
            'docker_agent':'docker_agent.KillService',
        }

        data = dict(
            initial_param = args, # two items : service , env_params
            executer = 'wta.executer.'+executer_map[configure['AGENT_NAME']],
        )

        print("## Killer data : ", data)
        rtn, rtn_message = ExecuterCaller.instance().execute_command(data)

        if rtn:
            status_code = status.HTTP_200_OK            
        else:
            status_code = status.HTTP_400_BAD_REQUEST

        return rtn_message, status_code

    post.permitted_roles = ["launcher"]

api.add_resource(Launcher, '/launch', endpoint='launch')
api.add_resource(Killer, '/kill', endpoint='kill')
