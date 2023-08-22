from flask_api import status
from flask_restful import reqparse
from miniagent import api
from miniagent.executer import ExecuterCaller
from miniagent.event_receiver import Resource

class GameStatus(Resource):

    def get(self, game_id, game_status):

        data = dict(
            initial_param = dict(
                game_id = game_id ,
                index = 'wta.game.status',
                filter_conditions = [
                    {"game_status": game_status},
                ],
            ),
            executer = 'wta.executer.opensearch_agent.Query',
        )

        rtn, rtn_message = ExecuterCaller.instance().execute_command(data)

        print("### rtn, rtn_message :",rtn, rtn_message)
        if rtn < 0:
            return rtn_message, status.HTTP_500_INTERNAL_SERVER_ERROR
        elif rtn == 0:
            return rtn_message, status.HTTP_204_NO_CONTENT

        return rtn_message['results'][0], status.HTTP_200_OK

    get.permitted_roles = ["opensearch_agent"]

class LatestBet(Resource):

    def get(self, game_id, account_id):

        data = dict(
            initial_param = dict(
                game_id = game_id ,
                index = 'wta.bet',
                sort_condition = { "bet_date": "desc"},
                filter_conditions = [
                    {"account_id": account_id},
                ],
                size = 1,
            ),
            executer = 'wta.executer.opensearch_agent.Query',
        )

        rtn, rtn_message = ExecuterCaller.instance().execute_command(data)
        
        if rtn < 0:
            return rtn_message, status.HTTP_500_INTERNAL_SERVER_ERROR
        elif rtn == 0 or not rtn_message['results']:
            return rtn_message, status.HTTP_204_NO_CONTENT

        return rtn_message['results'][0], status.HTTP_200_OK

    get.permitted_roles = ["opensearch_agent"]

class LatestCalcBet(Resource):

    def get(self, game_id):

        result = dict()

        data = dict(
            initial_param = dict(
                game_id = game_id ,
                index = 'wta.calc.bet',
                sort_condition = {"calc_date": "desc"},
                size = 1
            ),
            executer = 'wta.executer.opensearch_agent.Query',
        )

        rtn, rtn_message = ExecuterCaller.instance().execute_command(data)
        
        if rtn < 0:
            return rtn_message, status.HTTP_500_INTERNAL_SERVER_ERROR
        elif rtn == 0 or not rtn_message['results']: #Not Found
            return rtn_message, status.HTTP_204_NO_CONTENT

        result.update(rtn_message['results'][0])

        data = dict(
            initial_param = dict(
                game_id = game_id ,
                index = 'wta.calc.bet' ,
                dictinct_column = 'account_id' ,
            ),
            executer = 'wta.executer.opensearch_agent.Distinct',
        )

        rtn, rtn_message = ExecuterCaller.instance().execute_command(data)

        if rtn < 0:
            return rtn_message, status.HTTP_500_INTERNAL_SERVER_ERROR

        result.update(rtn_message)

        return result, status.HTTP_200_OK

    get.permitted_roles = ["opensearch_agent"]

class LatestRaffle(Resource):

    def get(self, game_id):

        data = dict(
            initial_param = dict(
                game_id = game_id ,
                index = 'wta.raffle',
                sort_condition = { "raffle_date": "desc"},
                size = 1,
            ),
            executer = 'wta.executer.opensearch_agent.Query',
        )

        rtn, rtn_message = ExecuterCaller.instance().execute_command(data)
        
        print("## rtn, rtn_message :", rtn, rtn_message)
        if rtn < 0:
            return rtn_message, status.HTTP_500_INTERNAL_SERVER_ERROR
        elif rtn == 0 or not rtn_message['results']:
            return rtn_message, status.HTTP_204_NO_CONTENT
        
        return rtn_message['results'][0], status.HTTP_200_OK

    get.permitted_roles = ["opensearch_agent"]

class RaffleList(Resource):

    def get(self, game_id):

        data = dict(
            initial_param = dict(
                game_id = game_id ,
                index = 'wta.raffle',
            ),
            executer = 'wta.executer.opensearch_agent.Query',
        )

        rtn, rtn_message = ExecuterCaller.instance().execute_command(data)
        
        if rtn < 0:
            return rtn_message, status.HTTP_500_INTERNAL_SERVER_ERROR
        elif rtn == 0 or not rtn_message['results']:
            return rtn_message, status.HTTP_204_NO_CONTENT
        
        return rtn_message, status.HTTP_200_OK

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
            executer = 'wta.executer.opensearch_agent.Query',
        )

        rtn, rtn_message = ExecuterCaller.instance().execute_command(data)

        if rtn < 0:
            return rtn_message, status.HTTP_500_INTERNAL_SERVER_ERROR
        elif rtn == 0:
            return rtn_message, status.HTTP_204_NO_CONTENT

        return rtn_message, status.HTTP_200_OK

    get.permitted_roles = ["opensearch_agent"]

api.add_resource(LatestBet, '/opensearch/latest_bet/<string:game_id>/<string:account_id>',\
                  endpoint='latest_bet')
api.add_resource(LatestCalcBet, '/opensearch/latest_calc_bet/<string:game_id>',\
                  endpoint='latest_calc_bet')
api.add_resource(LatestRaffle, '/opensearch/latest_raffle/<string:game_id>',\
                  endpoint='latest_raffle')
api.add_resource(RaffleList, '/opensearch/raffle_list/<string:game_id>',\
                  endpoint='raffle_list')
api.add_resource(CalcBetList, '/opensearch/calc_bet_list/<string:game_id>/<string:account_id>',\
                  endpoint='calc_bet_list')
api.add_resource(GameStatus, '/opensearch/game_status/<string:game_id>/<string:game_status>',\
                  endpoint='game_status')
