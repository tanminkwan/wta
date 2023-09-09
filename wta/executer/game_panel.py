from miniagent import configure
from miniagent.common import ExitType
from miniagent.executer import ExecuterInterface
from miniagent.adapters.kafka_producer import KafkaProducerAdapter
from miniagent.common import now

import logging

from datetime import datetime
from . import _get_game_info

class Prework(ExecuterInterface):

    def execute_command(self, 
                            initial_param: dict,
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
        configure['C_GAME_START_DATE'] = \
                datetime.fromisoformat(game_info['start_date'])

        return ExitType.STAY_RUNNING.value, {} 

class Deposit(ExecuterInterface):

    def execute_command(self, 
                            initial_param: dict, 
                            producer: KafkaProducerAdapter,
                        ) -> tuple[int, dict]:
        
        topic = 'wta.deposit'

        message = initial_param.copy()

        # dict or list must be converted to string
        bet_schedules = message.pop('bet_schedules')
        message.update({'bet_schedules':str(bet_schedules)})

        message.update(dict(
            game_id=configure['C_GAME_ID'],
            game_name=configure['C_GAME_NAME'],
            deposit_date=now().isoformat()),
        )

        print("## message : ", message)

        return producer.produce_message(
            topic= topic,
            message= message
            )