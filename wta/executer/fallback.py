from miniagent import configure
from miniagent.executer import ExecuterInterface
from miniagent.adapters.kafka_producer import KafkaProducerAdapter
from miniagent.adapters.rest_caller import RESTCaller
from miniagent.common import now, ExitType
import logging

from . import _get_url, _get_game_info

class Prework(ExecuterInterface):
    
    def execute_command(self, 
                            initial_param: dict,
                            rest_caller: RESTCaller,
                            producer: KafkaProducerAdapter,
                        ) -> tuple[int, dict]:

        rtn, game_info = _get_game_info()

        if rtn!=200:
            message = "_get_game_info error. rtn : " + str(rtn) + ", " + str(game_info)
            logging.error(message)
            return ExitType.ABNORMAL_EXIT.value, {'message':message}

        if game_info.get('game_status') != 'end':
            message = "Game is not over!!"
            logging.error(message)
            return ExitType.ABNORMAL_EXIT.value, {'message':message}

        configure['C_GAME_ID'] = game_info['game_id']
        configure['C_GAME_NAME'] = game_info['game_name']
                
        url = "http://"+_get_url('opensearch_agent')\
                 +"/opensearch/latest_fallback/" + configure.get('C_GAME_ID')
        
        rtn, result = rest_caller.call_get(url=url)

        base_date = ""
        if rtn == 200:
            base_date = result['bet_date']
        elif rtn == 204:
            base_date = game_info['end_date']
        else:
            message = "Error occures while getting latest_fallback."
            logging.error(message)
            return ExitType.ABNORMAL_EXIT.value, {'message':message}
        
        url = "http://"+_get_url('opensearch_agent')\
                 +"/opensearch/bets_to_cancel/" + configure.get('C_GAME_ID') + "/"\
                 +base_date        

        rtn, result = rest_caller.call_get(url=url)

        if rtn == 204:
            message = "There is no bets to cancel."
            logging.warning(message)
            return ExitType.NORMAL_EXIT.value, {'message':message} # It is normal.
        elif rtn != 200:
            message = "Error occures while getting bets_to_cancel. rtn : "+str(rtn)
            logging.error(message)
            return ExitType.ABNORMAL_EXIT.value, {'message':message}
        
        topic = 'wta.fallback'

        for rr in result['results']:

            message = rr.copy()
            message.update(dict(
                cancel_date=now().isoformat(),
                base_date=base_date
                )
            )

            producer.produce_message(
                topic= topic,
                message= message
            )

        return ExitType.STAY_RUNNING.value, result #job will be completed by itself