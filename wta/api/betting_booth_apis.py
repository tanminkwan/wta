from flask import request, make_response
from flask_restful import reqparse
from flask_api import status
from miniagent import api
from miniagent.executer import ExecuterCaller
from miniagent.event_receiver import Resource

class Bet(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('bet', type=dict)

    def post(self):

        args = Bet.parser.parse_args()

        data = dict(
            initial_param = args['bet'],
            executer = 'wta.executer.betting_booth.Bet',
        )

        rtn, rtn_message = ExecuterCaller.instance().execute_command(data)

        if rtn:
            status_code = status.HTTP_200_OK            
        else:
            status_code = status.HTTP_400_BAD_REQUEST

        return rtn_message, status_code

    post.permitted_roles = ["betting_booth"]

api.add_resource(Bet, '/betting_booth', endpoint='betting_booth')
