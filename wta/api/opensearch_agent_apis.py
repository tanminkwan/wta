from flask_api import status
from miniagent.executer import ExecuterCaller
from miniagent.event_receiver import Resource

class LatestCalcBet(Resource):

    def get(self, game_id):

        data = dict(
            initial_param = dict(
                game_id = game_id ,
            ),
            executer = 'wta.executer.opensearch_agent.LatestCalcBet',
        )

        rtn, rtn_message = ExecuterCaller.instance().execute_command(data)
        
        if rtn:
            status_code = status.HTTP_200_OK            
        else:
            status_code = status.HTTP_404_NOT_FOUND

        return rtn_message, status_code

    get.permitted_roles = ["opensearch_agent"]
