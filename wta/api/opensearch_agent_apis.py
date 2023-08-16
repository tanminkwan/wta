from flask_api import status
from flask_restful import reqparse
from miniagent import api
from miniagent.executer import ExecuterCaller
from miniagent.event_receiver import Resource

class LatestCalcBet(Resource):

    def get(self, game_id):

        result = dict()

        data = dict(
            initial_param = dict(
                game_id = game_id ,
                index = 'wta.calc.bet'
            ),
            executer = 'wta.executer.opensearch_agent.Latest',
        )

        rtn, rtn_message = ExecuterCaller.instance().execute_command(data)
        
        if rtn <= 0:
            return rtn_message, status.HTTP_500_INTERNAL_SERVER_ERROR

        result.update(rtn_message)

        data = dict(
            initial_param = dict(
                game_id = game_id ,
                index = 'wta.calc.bet' ,
                dictinct_column = 'account_id' ,
            ),
            executer = 'wta.executer.opensearch_agent.Distinct',
        )

        rtn, rtn_message = ExecuterCaller.instance().execute_command(data)

        if rtn == 404:
            return rtn_message, status.HTTP_404_NOT_FOUND
        elif rtn < 0:
            return rtn_message, status.HTTP_500_INTERNAL_SERVER_ERROR

        result.update(rtn_message)

        return result, status.HTTP_200_OK

    get.permitted_roles = ["opensearch_agent"]

class CalcBetList(Resource):

    def get(self, game_id, account_id):

        data = dict(
            initial_param = dict(
                game_id = game_id ,
                index = 'wta.calc.bet',
                filter_conditions = [
                    {"account_id": account_id},
                ],
                sort_condition = {"calc_date": "desc"},
            ),
            executer = 'wta.executer.opensearch_agent.FilterEqual',
        )

        rtn, rtn_message = ExecuterCaller.instance().execute_command(data)

        if rtn:
            status_code = status.HTTP_200_OK            
        else:
            status_code = status.HTTP_400_BAD_REQUEST

        return rtn_message, status_code

    get.permitted_roles = ["opensearch_agent"]

api.add_resource(LatestCalcBet, '/opensearch/latest_calc_bet/<string:game_id>',\
                  endpoint='latest_calc_bet')
api.add_resource(CalcBetList, '/opensearch/calc_bet_list/<string:game_id>/<string:account_id>',\
                  endpoint='calc_bet_list')
