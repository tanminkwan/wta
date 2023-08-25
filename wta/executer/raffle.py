from miniagent import configure
from miniagent.executer import ExecuterInterface
from miniagent.adapters.rest_caller import RESTCaller
from miniagent.adapters.kafka_producer import KafkaProducerAdapter

from datetime import datetime
from time import sleep
import logging
from . import _get_url, _get_game_info

class Prework(ExecuterInterface):

    def execute_command(self, 
                            initial_param: dict,
                            rest_caller: RESTCaller,
                        ) -> tuple[int, dict]:

        rtn, game_info = _get_game_info()

        if rtn!=200:
            logging.error("_get_game_info error. rtn : " + str(rtn))
            return -1, {}

        if game_info.get('game_status') == 'end':
            logging.error("Game is over!!")
            return -1, {}

        configure['C_GAME_ID'] = game_info['game_id']
        configure['C_GAME_NAME'] = game_info['game_name']

        while True:

            url = "http://"+_get_url('opensearch_agent')\
                    +"/opensearch/game_status/" + configure.get('C_GAME_ID') + "/publish"
            
            rtn, result = rest_caller.call_get(url=url)

            if rtn == 200:

                configure['C_RAFFLE_RULES'] = []
                RR = configure['C_RAFFLE_RULES']
                for rs in result['raffle_rules']:

                    funcs = {}
                    exec(rs['code'], funcs)
                    rs_f = funcs['f']

                    winner_count = 1
                    if rs.get('winner_count'):
                        winner_count = rs['winner_count'] \
                            if isinstance(rs['winner_count'],int) else int(rs['winner_count'])

                    RR.append(dict(
                        rule_name= rs['rule_name'],
                        code          = rs['code'],
                        function      = rs_f,
                        winning_type  = rs['winning_type'],
                        winning_point = rs['winning_point'] \
                            if isinstance(rs.get('winning_point'),int) else int(rs['winning_point']),
                        winner_count          = winner_count,
                        remaining_winner_count= winner_count,
                        end_immediately= True if rs.get('end_immediately') and rs['end_immediately']=='true' \
                            else False,
                    ))

                break
            else:
                logging.warning("Game Info is not found. rtn : "+str(rtn))
                sleep(10)

        url = "http://"+_get_url('opensearch_agent')\
                 +"/opensearch/latest_raffle/" + configure.get('C_GAME_ID')
        
        rtn, result = rest_caller.call_get(url=url)

        status = {}

        if rtn == 200 and result.get('status'):

            rs = result['status']
                
            status = {item['rule_name']: item['remaining_winner_count'] for item in rs}

        for rr in configure['C_RAFFLE_RULES']:

            if rr['rule_name'] in status:
                rr["remaining_winner_count"] = status[rr['rule_name']]

        print("### configure['C_RAFFLE_RULES'] : ", configure['C_RAFFLE_RULES'])
        return 1, result
"""
class RaffleRule(ExecuterInterface):

    def execute_command(self, 
                            initial_param: dict,
                            producer: KafkaProducerAdapter,
                        ) -> tuple[int, dict]:
        
        topic = 'wta.raffle.rule'
        
        if initial_param.get('game_id') != configure.get('C_GAME_ID'):
            return 0, {'message':'Game Id is wrong.'}

    def _update_raffle_rule(self, raffle_rule:dict) -> dict:

        funcs = {}
        exec(raffle_rule['code'], funcs)
        f = funcs['f']
        raffle_rule['function'] = f

        for rr in configure['C_RAFFLE_RULES']:

            if raffle_rule['rule_name']==rr.get('rule_name') \
                and rr['remaining_winner_count']>0:
    
                rr['code'] = raffle_rule['code']
                rr['function'] = raffle_rule['function']
                rr['winning_type'] = raffle_rule['winning_type']
                rr['winning_point'] = raffle_rule['winning_point']
                rr['winner_count'] = raffle_rule['winner_count']
    
                if rr['winner_count'] < rr['remaining_winner_count']:
                    rr['remaining_winner_count'] = rr['winner_count']
"""
class Raffle(ExecuterInterface):

    def execute_command(self, 
                            initial_param: dict,
                            producer: KafkaProducerAdapter,
                        ) -> tuple[int, dict]:
        
        topic = 'wta.raffle'
        
        if initial_param.get('game_id') != configure.get('C_GAME_ID'):
            return 0, {'message':'Game Id is wrong.'}

        is_raffled, message = self._check_raffle_rules(initial_param.copy())
        
        print("## message : ", is_raffled, message)

        if is_raffled:
            return producer.produce_message(
                topic= topic,
                message= message
                )
        else:
            return 0, {'message':message}
    
    def _check_raffle_rules(self, calc_bet:dict) -> dict:

        is_raffled = False        
        
        calc_bet.update({"winnings":[],"status":[],"raffle_date":datetime.now().isoformat()})

        for rr in configure['C_RAFFLE_RULES']:

            params = {}

            if rr['remaining_winner_count'] > 0:                

                f = rr['function']
                val_names = f.__code__.co_varnames

                for item in calc_bet:
                    if item in val_names:
                        params.update({item:calc_bet[item]})

                if f(**params):
                    is_raffled = True
                    rr['remaining_winner_count'] -= 1
                    calc_bet['winnings'].append(rr['rule_name'])

            t = dict(
                rule_name = rr['rule_name'],
                winner_count = rr['winner_count'],
                remaining_winner_count = rr['remaining_winner_count'],
                end_immediately = rr['end_immediately'] if rr.get('end_immediately') else False
            )

            calc_bet['status'].append(t)

        return is_raffled, calc_bet