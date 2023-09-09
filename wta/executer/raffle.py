from miniagent import configure
from miniagent.common import ExitType
from miniagent.executer import ExecuterInterface
from miniagent.adapters.rest_caller import RESTCaller
from miniagent.adapters.kafka_producer import KafkaProducerAdapter
from miniagent.common import now
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
            return ExitType.ABNORMAL_EXIT.value, {}

        if game_info.get('game_status') == 'end':
            logging.error("Game is over!!")
            return ExitType.NORMAL_EXIT.value, {}

        configure['C_GAME_ID'] = game_info['game_id']
        configure['C_GAME_NAME'] = game_info['game_name']

        while True:

            url = "http://"+_get_url('opensearch_agent')\
                    +"/opensearch/game_status/" + configure.get('C_GAME_ID') + "/publish"
            
            rtn, result = rest_caller.call_get(url=url)

            print("### game_status url, rtn, result : ", url, rtn, result)
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
        return ExitType.STAY_RUNNING.value, result

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
        
        calc_bet.update({"winnings":[],"status":[],"raffle_date":now().isoformat()})

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