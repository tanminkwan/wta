from miniagent import configure
from miniagent.common import ExitType
from miniagent.executer import ExecuterInterface
from miniagent.adapters.rest_caller import RESTCaller
import logging

from . import _get_url, _get_game_info

class Prework(ExecuterInterface):

    def execute_command(self, 
                            initial_param: dict,
                            rest_caller: RESTCaller,
                        ) -> tuple[int, dict]:

        rtn, game_info = _get_game_info()

        if rtn!=200:
            logging.error("_get_game_info error. rtn : " + str(rtn) + "[]" + str(game_info))
            return ExitType.ABNNORMAL_EXIT.value, {}

        if game_info.get('game_status') == 'publish':
            logging.error("The game hasn't started yet!!")
            return ExitType.ABNNORMAL_EXIT.value, {}

        if game_info.get('game_status') == 'end':
            logging.error("Game is over!!")
            return ExitType.NORMAL_EXIT.value, {}

        configure['C_GAME_ID'] = game_info['game_id']
        configure['C_GAME_NAME'] = game_info['game_name']
        
        url = "http://"+_get_url('opensearch_agent')\
                 +"/opensearch/latest_bet/" + configure.get('C_GAME_ID') + '/' \
                 + configure.get('C_ACCOUNT_ID')
        
        rtn, result = rest_caller.call_get(url=url)

        if rtn == 200 and result.get('account_id'):

            if result['deposit_balance'] <= 0:
                logging.error("deposit_balance is zero.")
                return ExitType.NORMAL_EXIT.value, {}

            configure['C_DEPOSIT_BALANCE'] = result['deposit_balance']
            configure['C_BET_SEQ'] = result['bet_seq']

        return ExitType.STAY_RUNNING.value, result

class RequestBet(ExecuterInterface):

    def execute_command(self, 
                            initial_param: dict,
                            rest_caller: RESTCaller,
                        ) -> tuple[int, dict]:
        
        #is_lasttime = False
        if not configure.get('C_DEPOSIT_BALANCE'):
           configure['C_DEPOSIT_BALANCE'] = configure['C_DEPOSIT_AMOUNT']

        if configure['C_DEPOSIT_BALANCE'] <= 0:

            return -1, dict(error="Balance is zero.")
        
        elif configure['C_DEPOSIT_BALANCE'] - initial_param['bet_amount'] <= 0:
            #is_lasttime = True
            bet_amount = configure['C_DEPOSIT_BALANCE']
        else:
            bet_amount = initial_param['bet_amount']

        deposit_balance = configure['C_DEPOSIT_BALANCE'] - bet_amount
        bet_seq = configure['C_BET_SEQ'] + 1
        
        param = dict(
            game_id = configure.get('C_GAME_ID'),
            game_name = configure.get('C_GAME_NAME'),
            account_id = configure.get('C_ACCOUNT_ID'),
            game_user_name = configure.get('C_GAME_USER_NAME'),
            bet_seq = bet_seq,
            bet_amount = bet_amount,
            deposit_balance = deposit_balance,
            deposit_amount  = configure['C_DEPOSIT_AMOUNT'],
            expected_bet_count = len(configure['C_BET_SCHEDULES']),
        )

        print("### param : ", param)
        url = "http://"+_get_url('betting_booth')+"/betting_booth"
        
        try:
            rtn, results = rest_caller.call_post(
                        url=url, 
                        json={"bet":param}
                    )
        except Exception as e:
            logging.error('Exception : ' + e.__str__())
            return -1, dict(error=e.__str__())
        
        if rtn >= 200 and rtn < 300:

            configure['C_BET_SEQ'] = bet_seq
            configure['C_DEPOSIT_BALANCE'] = deposit_balance

            #if is_lasttime:
            #    from miniagent import scheduler
            #    scheduler.remove_job(initial_param['job_id'])

        return rtn, results