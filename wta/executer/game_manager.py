from miniagent import configure
from miniagent.executer import ExecuterInterface
from miniagent.adapters.kafka_producer import KafkaProducerAdapter
from miniagent.adapters.rest_caller import RESTCaller

import uuid
import logging
from datetime import datetime, timedelta

from . import _get_url, _get_game_info

def _set_game_info(rest_caller, game_info):

    url = "http://"+_get_url('config_map')+"/config_map"
        
    try:
        rtn, results = rest_caller.call_post(
                        url=url, 
                        json={"config_map":game_info}
                    )
    except Exception as e:
        logging.error('Exception : ' + e.__str__())
        return -1
        
    if rtn == 200:
        return 1
    else:
        return -2

class Game(ExecuterInterface):

    def _set_start_game_job(self, signup_date, start_date):

        from miniagent import scheduled_job

        job_signup = {
            "executer":"wta.executer.game_manager.Start",
            "trigger":"date",
            "id":"signup",
            "name":"Signup",
            "params":{"game_status":"signup"},
            "run_date":signup_date,
        }

        scheduled_job._run_job(job_signup)

        job_start = {
            "executer":"wta.executer.game_manager.Start",
            "trigger":"date",
            "id":"start_game",
            "name":"Start Game",
            "params":{"game_status":"start"},
            "run_date":start_date,
        }

        scheduled_job._run_job(job_start)

        return

    def execute_command(self, 
                            initial_param: dict, 
                            producer: KafkaProducerAdapter,
                            rest_caller: RESTCaller,
                        ) -> tuple[int, dict]:
        
        rtn, game_info = _get_game_info()

        print("### rtn, game_info : ",rtn, game_info)
        if rtn==204:
            logging.warning("There is no game info")
        elif rtn != 200:
            message = "_get_game_info error. rtn : "+str(rtn)
            logging.error(message)
            return -1, {"message":message}
        elif game_info.get('game_status') != 'end':
            message = "Game is not over!!"
            logging.error(message)
            return -1, {"message":message}
    
        topic = 'wta.game.status'
        now =  datetime.now()

        configure['C_GAME_ID']     =uuid.uuid4().hex
        configure['C_GAME_NAME']   =initial_param['game_name']
        configure['C_RAFFLE_RULES']=initial_param['raffle_rules']

        signup_date = datetime.strptime(initial_param['signup_date'], "%Y-%m-%dT%H:%M")
        start_date = datetime.strptime(initial_param['start_date'], "%Y-%m-%dT%H:%M")

        self._set_start_game_job(signup_date, start_date)

        message = initial_param.copy()
        message.update(dict(
            create_date=now.isoformat(),
            game_id=configure['C_GAME_ID'],
            game_status='publish',
            ))

        game_info = dict(
            game_id=message['game_id'],
            game_name=message['game_name'],
            create_date=message['create_date'],
            game_status=message['game_status'],
        )

        _set_game_info(rest_caller, game_info)

        return producer.produce_message(
            topic= topic,
            message= message
            )

class Start(ExecuterInterface):

    def execute_command(self, 
                            initial_param: dict, 
                            rest_caller: RESTCaller,
                            producer: KafkaProducerAdapter,
                        ) -> tuple[int, dict]:

        topic = 'wta.game.status'
        now =  datetime.now()
        if not initial_param.get('game_status'):
            logging.warning('game_status value is empty. Job start is canceled.')
        
        message = dict(
            create_date=now.isoformat(),
            game_id=configure['C_GAME_ID'],
            game_name=configure['C_GAME_NAME'],
            game_status=initial_param['game_status'],
            )

        print("## Start message : ", message)
        _set_game_info(rest_caller, message)

        return producer.produce_message(
            topic= topic,
            message= message
            )

class End(ExecuterInterface):

    def _check_end(self, initial_param):

        status = initial_param['status']

        is_ended = False
        for st in status:

            if st['remaining_winner_count']==0 and st['end_immediately'] == True:
                is_ended = True
                break

        return is_ended
    
    def _get_winnings(self, initial_param, rest_caller):

        url = "http://"+_get_url('opensearch_agent')\
                 +"/opensearch/raffle_list/" + initial_param['game_id']
        
        rtn, result = rest_caller.call_get(url=url)

        winnings_list = []

        if rtn == 200 and result.get('results'):

            rr_dict = {item["rule_name"]: item for item in configure['C_RAFFLE_RULES']}
        
            for rr in result['results']:
                
                for rule_name in rr['winnings']:

                    raffle_rule = rr_dict[rule_name]

                    if raffle_rule['winning_point'] <= 0: # Zero winnings
                        continue

                    winnings = 0
                    if raffle_rule['winning_type']=='percentage':
                        winnings = round(( raffle_rule['winning_point'] \
                                          * initial_param['tot_bet_amount'] )/ 100)
                    elif raffle_rule['winning_type']=='quantity':
                        winnings = raffle_rule['winning_point']
                        
                    winnings_list.append(dict(
                        winnings = winnings,
                        rule_name = rule_name,
                        account_id = rr['account_id'],
                        game_user_name = rr['game_user_name'],
                        bet_seq = rr['bet_seq'],
                        bet_amount = rr['bet_amount'],
                        bet_date = rr['bet_date'],
                    ))

        return winnings_list

    def execute_command(self, 
                            initial_param: dict, 
                            producer: KafkaProducerAdapter,
                            rest_caller: RESTCaller,
                        ) -> tuple[int, dict]:
        
        topic = 'wta.game.status'
        now =  datetime.now()

        if not self._check_end(initial_param):
            return 0, {'message':'Still Running'}
        
        winnings = self._get_winnings(initial_param, rest_caller)

        message = dict(
            game_id=initial_param['game_id'],
            game_name=initial_param['game_name'],
            game_status='end',
            end_date=initial_param['raffle_date'],
            winnings=winnings,
            create_date=now.isoformat(),
            )

        print("## end message : ", message)

        game_info = dict(
            game_id=message['game_id'],
            game_name=message['game_name'],
            create_date=message['create_date'],
            game_status=message['game_status'],
        )

        _set_game_info(rest_caller, game_info)

        return producer.produce_message(
            topic= topic,
            message= message
            )
