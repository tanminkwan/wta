from flask import request
from flask_restful import reqparse
from flask_api import status
from miniagent import api, app
from miniagent.executer import ExecuterCaller
from miniagent.event_receiver import Resource

class Prompt(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('prompt', type=dict)

    def post(self):

        args = Prompt.parser.parse_args()

        data = dict(
            initial_param = dict(
                prompt = args['prompt'],
            ),
            executer = 'wta.executer.openai_agent.Prompt',
        )

        rtn, rtn_message = ExecuterCaller.instance().execute_command(data)

        if rtn:
            status_code = status.HTTP_200_OK            
        else:
            status_code = status.HTTP_400_BAD_REQUEST

        return rtn_message, status_code

    post.permitted_roles = ["openai_agent"]

api.add_resource(Prompt, '/openai_agent/prompt', endpoint='prompt')
