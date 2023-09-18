from miniagent import configure
from miniagent.executer import ExecuterInterface
from miniagent.adapters.opensearch_caller import OpensearchCaller
from datetime import datetime, timedelta
import logging

url = "http://"+configure.get('ELASTIC_SEARCH_DOMAIN_NAME')\
            +":"+configure.get('ELASTIC_SEARCH_PORT')

class Query(ExecuterInterface):

    def _parcer(self, response):

        if not response['hits']['hits']:
            return 0, {"results":[]}

        results = []
        
        for q in response['hits']['hits']:
            results.append(q['_source'])

        return 1, {"results":results}

    def execute_command(self, 
                            initial_param: dict,
                            os_caller: OpensearchCaller,
                        ) -> tuple[int, dict]:
        
        index = initial_param['index']
        query =\
        {
            "query": {
                "bool": {
                    "must": []
                }
            }
        }

        if initial_param.get('bool'):
                    
            for q in initial_param['bool']:

                query['query']['bool']['must'].append({"match": q})
        
        if initial_param.get('sort'):

            query.update(dict(
                sort = initial_param['sort'])
            )

        if initial_param.get('size'):

            query.update(dict(
                size = initial_param['size'])
            )

        if initial_param.get('range'):

            query['query']['bool']['must'].append(dict(
                range = initial_param['range'])
            )

        print("### query : ", query)

        return os_caller.call_get(url, index, query, self._parcer)

class IndividualStat(ExecuterInterface):

    def _get_individual_stat(self, os_caller, game_id, account_id):

        params = dict(
                index = 'wta.calc.bet',
                bool = [
                    {"game_id":game_id},
                    {"account_id":account_id},
                ],
                sort = { "calc_date": "desc"},
                size = 1,
            )

        rtn, results = Query().execute_command(params, os_caller)

        if results.get('results'):
            tmp = results['results'][0]
            result = dict(
                deposit_amount = tmp['deposit_amount'],
                deposit_balance = tmp['deposit_balance'],
                bet_amount = tmp['deposit_amount'] - tmp['deposit_balance'],
                bet_count = tmp['bet_seq'],
                expected_bet_count = tmp['expected_bet_count'] if tmp.get('expected_bet_count') else 100,
            )
        else:
            result = dict(
                deposit_amount = 0,
                deposit_balance = 0,
                bet_amount = 0,
                bet_count = 0,
                expected_bet_count = 0
            )

        return result

    def execute_command(self, 
                            initial_param: dict,
                            os_caller: OpensearchCaller,
                        ) -> tuple[int, dict]:
        
        game_id = initial_param['game_id']
        account_id = initial_param['account_id']

        individual_stat = self._get_individual_stat(os_caller, game_id, account_id)

        return 1, individual_stat
    
class BetSchedules(ExecuterInterface):

    def _get_game_info(self, os_caller, game_id):

        params = \
            dict(
                index = 'wta.game.status',
                bool = [
                    {"game_id":game_id},
                    {"game_status":"publish"},
                ]
            )

        rtn, results = Query().execute_command(params, os_caller)
        return results['results'] if results.get('results') else []

    def _get_bet_schedules(self, os_caller, game_id):

        params = \
            dict(
                index = 'wta.deposit',
                bool = [
                    {"game_id":game_id}
                ]
            )

        rtn, results = Query().execute_command(params, os_caller)
        return results['results'] if results.get('results') else []
    
    def _get_bet_starts(self, os_caller, game_id):

        params = \
            dict(
                index = 'wta.calc.bet',
                bool = [
                    {"game_id":game_id},
                    {"bet_seq":1},
                ]
            )

        rtn, results = Query().execute_command(params, os_caller)
        return results['results'] if results.get('results') else []
    
    def _adjusted_bet_schedules(self, game_info, bet_schedules, bet_starts):

        if not game_info:
            return []
        
        game_start_date = datetime.fromisoformat(game_info[0]['start_date'])
        
        map = {item["account_id"]: \
               round((datetime.fromisoformat(item["calc_date"])\
                       - game_start_date).total_seconds())  for item in bet_starts}
        
        adjusted_bet_schedules = []

        for deposit in bet_schedules:
            if not map.get(deposit['account_id']):
                continue

            print("$$ deposit['bet_schedules'] : ",deposit['bet_schedules'])
            bss = eval(deposit['bet_schedules'])
            init_wait = bss[0]['waiting_secs'];
            for bs in bss:
                bs['waiting_secs'] = bs['waiting_secs'] + map[deposit['account_id']] - init_wait
            print("$$ bss : ", bss)

            adjusted_bet_schedules.append(dict(
                game_user_name = deposit['game_user_name'],
                account_id = deposit['account_id'],
                deposit_amount = deposit['deposit_amount'],
                bet_schedules = bss,
            ))

        return adjusted_bet_schedules

    def execute_command(self, 
                            initial_param: dict,
                            os_caller: OpensearchCaller,
                        ) -> tuple[int, dict]:
        
        game_id = initial_param['game_id']

        game_info = self._get_game_info(os_caller, game_id)
        bet_schedules = self._get_bet_schedules(os_caller, game_id)
        bet_starts    = self._get_bet_starts(os_caller, game_id)

        bet_schedules = self._adjusted_bet_schedules(game_info, bet_schedules, bet_starts)
        
        return 1, {'results':bet_schedules}

class TotStat(ExecuterInterface):

    def _get_winning_info(self, os_caller, game_id):

        params = \
            dict(
                index = 'wta.game.status',
                bool = [
                    {"game_id":game_id},
                    {"game_status":"end"},
                ]
            )

        rtn, results = Query().execute_command(params, os_caller)
        return results['results'][0]['winnings'] if results['results'] else []

    def _get_game_info(self, os_caller, game_id):

        params = \
            dict(
                index = 'wta.game.status',
                bool = [
                    {"game_id":game_id},
                    {"game_status":"publish"},
                ]
            )

        rtn, results = Query().execute_command(params, os_caller)
        return results['results'] if results.get('results') else []

    def _get_last_calc(self, os_caller, game_id):

        params = dict(
                index = 'wta.calc.bet',
                bool = [
                    {"game_id":game_id}
                ],
                sort = { "calc_date": "desc"},
                size = 1,
            )

        rtn, results = Query().execute_command(params, os_caller)

        if rtn > 0:
            result = results['results'][0]
        else:
            result = {}

        return result
    
    def _get_last_raffle(self, os_caller, game_id):

        params = dict(
                index = 'wta.raffle',
                bool = [
                    {"game_id":game_id}
                ],
                sort = { "raffle_date": "desc"},
                size = 1,
            )

        rtn, results = Query().execute_command(params, os_caller)

        if rtn > 0:
            result = results['results'][0]
        else:
            result = {}

        return result

    def _tot_stat(self, game_info, last_calc, last_raffle, awards):

        if not game_info:
            return []
        
        raffle_rules = game_info[0]['raffle_rules']

        map = {rr["rule_name"]: \
               dict(
                    winning_point = rr['winning_point'],
                    winning_type  = rr['winning_type'],
                    winner_count  = rr['winner_count'],
               ) \
                for rr in raffle_rules if rr["winning_point"] > 0}

        map2 = {}
        if last_raffle.get('status'):
            map2 = {rr["rule_name"]: \
                dict(
                        remaining_winner_count  = rr['remaining_winner_count'],
                ) \
                    for rr in last_raffle['status']}        

        raffle_stats = []
        for rs in raffle_rules:

            if rs["winning_point"] <= 0:
                continue

            if map2.get(rs['rule_name']):
                remaining_winner_count = map2[rs['rule_name']]['remaining_winner_count']
            else:
                remaining_winner_count = rs['winner_count']

            winnings = 0

            tot_bet_amount = last_calc['tot_bet_amount'] if last_calc.get('tot_bet_amount') else 0

            if rs['winning_type']=='percentage':
                winnings = round(( rs['winning_point'] \
                                * tot_bet_amount )/ 100)
            else:
                winnings = rs['winning_point']

            tmp = {}
            tmp.update(rs)
            tmp.pop("code")
            tmp.update(map[rs['rule_name']])
            tmp.update({"winnings":winnings,"remaining_winner_count":remaining_winner_count})
            raffle_stats.append(tmp)

        """
        if last_raffle:

            for rs in last_raffle['status']:

                if map.get(rs['rule_name']):

                    winnings = 0
                    if map[rs['rule_name']]['winning_type']=='percentage':
                        winnings = round(( map[rs['rule_name']]['winning_point'] \
                                        * last_calc['tot_bet_amount'] )/ 100)
                    else:
                        winnings = map[rs['rule_name']]['winning_point']

                    tmp = {}
                    tmp.update(rs)
                    tmp.update(map[rs['rule_name']])
                    tmp.update({"winnings":winnings})
                    raffle_stats.append(tmp)
        """
        tot_stat = {}
        if last_calc:

            tot_stat = dict(
                tot_deposit_amount = last_calc['tot_deposit_amount'],
                tot_deposit_balance = last_calc['tot_deposit_balance'],
                tot_bet_amount = last_calc['tot_bet_amount'],
                tot_bet_count = last_calc['tot_bet_count'],
                account_count = last_calc['account_count'],
                tot_expected_bet_count = last_calc['tot_expected_bet_count'],
                avg_deposit_amount_per_account = last_calc['avg_deposit_amount_per_account'],
                avg_bet_amount_per_account = last_calc['avg_bet_amount_per_account'],
                avg_bet_amount_per_round = last_calc['avg_bet_amount_per_round'],
            )
        else:
            tot_stat = dict(
                tot_deposit_amount = 0,
                tot_deposit_balance = 0,
                tot_bet_amount = 0,
                tot_bet_count = 0,
                account_count = 0,
                tot_expected_bet_count = 0,
                avg_deposit_amount_per_account = 0,
                avg_bet_amount_per_account = 0,
                avg_bet_amount_per_round = 0,
            )
        
        return dict(
            tot_stat=tot_stat,
            raffle_stats=raffle_stats,
            awards=awards,
        )

    def execute_command(self, 
                            initial_param: dict,
                            os_caller: OpensearchCaller,
                        ) -> tuple[int, dict]:
        
        game_id = initial_param['game_id']

        game_info     = self._get_game_info(os_caller, game_id)
        last_calc     = self._get_last_calc(os_caller, game_id)
        print("$$ last_calc :",last_calc)
        last_raffle   = self._get_last_raffle(os_caller, game_id)
        print("$$ last_calc :",last_raffle)
        awards  = self._get_winning_info(os_caller, game_id)
        tot_stat = self._tot_stat(game_info, last_calc, last_raffle, awards)
        print("$$ tot_stat :",tot_stat)

        return 1, tot_stat

class Distinct(ExecuterInterface):

    def _parcer(self, response):

        q = response.get('aggregations').get('unique_names').get('buckets')
        
        qq = [ row['key'] for row in q ]

        return {"accounts":qq}

    def execute_command(self, 
                            initial_param: dict,
                            os_caller: OpensearchCaller,
                        ) -> tuple[int, dict]:
        
        index = initial_param['index']
        query =\
        {
            "query": {
                "match": {
                    "game_id": initial_param['game_id']
                }
            },  
            "aggs":{
                "unique_names": {
                    "terms": {
                        "field": initial_param['dictinct_column']+".keyword"
                    }
                }
            },
            "_source": False
        }

        return os_caller.call_get(url, index, query, self._parcer)
