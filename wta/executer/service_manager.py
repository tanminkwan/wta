from miniagent import configure
from miniagent.executer import ExecuterInterface
from miniagent.adapters.rest_caller import RESTCaller
from miniagent.adapters.kafka_producer import KafkaProducerAdapter
import logging

from datetime import datetime
from . import _get_url, _get_game_info

class Prework(ExecuterInterface):

    def execute_command(self, 
                            initial_param: dict,
                        ) -> tuple[int, dict]:
        
        rtn, game_info = _get_game_info()

        if rtn!=200:
            logging.error("_get_game_info error. rtn : " + str(rtn))
            return -1, {}

        configure['C_GAME_ID'] = game_info['game_id']
        configure['C_GAME_NAME'] = game_info['game_name']

        print("## C_GAME_ID : ", configure['C_GAME_ID'])
        print("## C_GAME_NAME : ", configure['C_GAME_NAME'])
        
        return 1, {} 

class Status(ExecuterInterface):

    def execute_command(self, 
                            initial_param: dict,
                        ) -> tuple[int, dict]:

        rtn, game_info = _get_game_info()

        if rtn!=200:
            logging.error("_get_game_info error. rtn : " + str(rtn))
            return -1, {}

        if initial_param.get('game_id') != game_info['game_id']:
            return 0, {'message':'Game Id is wrong.'}

        configure['C_GAME_ID'] = game_info['game_id']
        configure['C_GAME_NAME'] = game_info['game_name']

        #print("Status : ", initial_param)

        return 1, {} 

class Deposit(ExecuterInterface):

    def _create_betting_agent(self, rest_caller, launch_info):

        url = "http://"+_get_url('k8s_agent')+"/launch"

        try:
            rtn, result = rest_caller.call_post(
                            url=url, 
                            json=launch_info
                        )
        except Exception as e:
            message = "Exception : " + e.__str__()
            logging.error(message)
            return -1, {"error":message}
            
        if rtn == 200:
            return 1, result
        else:
            return -1, {"error":result}

    def execute_command(self, 
                            initial_param: dict,
                            rest_caller: RESTCaller,
                        ) -> tuple[int, dict]:        

        if initial_param.get('game_id') != configure.get('C_GAME_ID'):
            return 0, {'message':'Game Id is wrong.'}
        
        env_params = initial_param.copy()

        service = 'betting_agent'
        env_params.update(
            agent_name='betting_agent.'+env_params['account_id'],
            agent_roles='betting_agent'
        )

        launch_info = dict(
            service = service,
            env_params = env_params
        )

        rtn, result = self._create_betting_agent(rest_caller, launch_info)
        
        return rtn, result