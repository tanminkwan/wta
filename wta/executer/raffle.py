from miniagent import configure
from miniagent.executer import ExecuterInterface
from miniagent.adapters.rest_caller import RESTCaller
from miniagent.adapters.kafka_producer import KafkaProducerAdapter

from datetime import datetime
from . import _get_url


class Prework(ExecuterInterface):

    def execute_command(self, 
                            initial_param: dict,
                            rest_caller: RESTCaller,
                        ) -> tuple[int, dict]:

        url = "http://"+_get_url('opensearch_agent')\
                 +"/opensearch/latest_raffle/" + configure.get('C_GAME_ID')
        
        rtn, result = rest_caller.call_get(url=url)

        status = {}

        if rtn == 200 and result.get('status'):

            rs = result['status']
                
            status = {item['raffle_rule_id']: item['remaining_winner_count'] for item in rs}

        for rr in configure['C_RAFFLE_RULES']:

            funcs = {}
            exec(rr['code'], funcs)
            f = funcs['f']
            rr['function'] = f

            if rr['raffle_rule_id'] in status:
                rr["remaining_winner_count"] = status[rr['raffle_rule_id']]

        print("### configure['C_RAFFLE_RULES'] : ", configure['C_RAFFLE_RULES'])
        return 1, result

class Raffle(ExecuterInterface):

    def execute_command(self, 
                            initial_param: dict,
                            producer: KafkaProducerAdapter,
                        ) -> tuple[int, dict]:
        
        topic = 'wta.raffle'
        print("## initial_param : ", initial_param)

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
                    calc_bet['winnings'].append(rr['raffle_rule_id'])

            t = dict(
                raffle_rule_id = rr['raffle_rule_id'],
                winner_count = rr['winner_count'],
                remaining_winner_count = rr['remaining_winner_count'],
            )

            calc_bet['status'].append(t)

        return is_raffled, calc_bet