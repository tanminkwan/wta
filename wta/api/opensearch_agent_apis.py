from flask_api import status
from flask_restful import reqparse
from miniagent import api
from miniagent.executer import ExecuterCaller
from miniagent.event_receiver import Resource

class GameStatus(Resource):

    def get(self, game_id, game_status):

        data = dict(
            initial_param = dict(
                index = 'wta.game.status',
                bool = [
                    {"game_id":game_id},
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
                index = 'wta.bet',
                bool = [
                    {"account_id": account_id},
                    {"game_id":game_id}
                ],
                sort = { "bet_date": "desc"},
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
                index = 'wta.calc.bet',
                bool = [
                    {"game_id":game_id}
                ],
                sort = {"calc_date": "desc"},
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
                index = 'wta.raffle',
                bool = [
                    {"game_id":game_id}
                ],
                sort = { "raffle_date": "desc"},
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
                index = 'wta.raffle',
                bool = [
                    {"game_id":game_id}
                ],
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
                index = 'wta.calc.bet',
                bool = [
                    {"account_id": account_id},
                    {"game_id":game_id}
                ],
                sort = {"calc_date": "desc"},
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

class LatestFallback(Resource):

    def get(self, game_id):

        data = dict(
            initial_param = dict(
                index = 'wta.fallback',
                bool = [
                    {"game_id":game_id}
                ],
                sort = { "cancel_date": "desc"},
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

class CurrentStats(Resource):

    def get(self, game_id, account_id):
        
        param1 = dict(
            initial_param = dict(
                game_id = game_id,
                account_id = account_id,
            ),
            executer = 'wta.executer.opensearch_agent.IndividualStat',
        )

        rtn, individual_stat = ExecuterCaller.instance().execute_command(param1)

        param2 = dict(
            initial_param = dict(
                game_id = game_id,
            ),
            executer = 'wta.executer.opensearch_agent.BetSchedules',
        )

        rtn, bet_schedules = ExecuterCaller.instance().execute_command(param2)

        param3 = dict(
            initial_param = dict(
                game_id = game_id,
            ),
            executer = 'wta.executer.opensearch_agent.TotStat',
        )

        rtn, tot_stat = ExecuterCaller.instance().execute_command(param3)

        return dict(
                    individual_stat = individual_stat,
                    bet_schedules = bet_schedules['results'],
                    tot_stat = tot_stat,
                ), status.HTTP_200_OK

    get.permitted_roles = ["opensearch_agent", "cache"]

class Bets2Cancel(Resource):

    def get(self, game_id, base_date):

        data = dict(
            initial_param = dict(
                index = 'wta.bet',
                bool = [
                    {"game_id":game_id}
                ],
                range = {"bet_date": {"gt": base_date}},
                sort = {"bet_date": "asc"},
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
api.add_resource(LatestFallback, '/opensearch/latest_fallback/<string:game_id>',\
                  endpoint='latest_fallback')
api.add_resource(Bets2Cancel, '/opensearch/bets_to_cancel/<string:game_id>/<string:base_date>',\
                  endpoint='bets_to_cancel')
api.add_resource(RaffleList, '/opensearch/raffle_list/<string:game_id>',\
                  endpoint='raffle_list')
api.add_resource(CalcBetList, '/opensearch/calc_bet_list/<string:game_id>/<string:account_id>',\
                  endpoint='calc_bet_list')
api.add_resource(GameStatus, '/opensearch/game_status/<string:game_id>/<string:game_status>',\
                  endpoint='game_status')
api.add_resource(CurrentStats, '/opensearch/current_stat/<string:game_id>/<string:account_id>',\
                  endpoint='current_stat')


