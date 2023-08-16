from miniagent import configure
from miniagent.executer import ExecuterInterface
from miniagent.adapters.kafka_producer import KafkaProducerAdapter

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
        params = {}
        calc_bet.update({"winnings":[]})

        for rr in configure['C_RAFFLE_RULES']:

            if rr['remaining_winner_count'] < 1:
                continue

            f = rr['function']
            val_names = f.__code__.co_varnames

            for item in calc_bet:
                if item in val_names:
                    params.update({item:calc_bet[item]})

            if f(**params):
                is_raffled = True
                rr['remaining_winner_count'] -= 1
                t = rr.copy()
                t.pop('function')
                t.pop('code')
                calc_bet['winnings'].append(t)

        return is_raffled, calc_bet