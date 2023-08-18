from miniagent import configure
from miniagent.executer import ExecuterInterface
from miniagent.adapters.rest_caller import RESTCaller
import logging
import os

from . import _get_url

class Prework(ExecuterInterface):

    def execute_command(self, 
                            initial_param: dict,
                            rest_caller: RESTCaller,
                        ) -> tuple[int, dict]:

        url = "http://"+_get_url('opensearch_agent')\
                 +"/opensearch/latest_bet/" + configure.get('C_GAME_ID') + '/' \
                 + configure.get('C_ACCOUNT_ID')
        
        rtn, result = rest_caller.call_get(url=url)

        if rtn == 200 and result.get('account_id'):

            if result['deposit_balance'] <= 0:
                logging.info("deposit_balance is zero.")
                os._exit(1)

            configure['C_DEPOSIT_BALANCE'] = result['deposit_balance']
            configure['C_BET_SEQ'] = result['bet_seq']
                   
        return 1, result

class RequestBet(ExecuterInterface):

    def execute_command(self, 
                            initial_param: dict,
                            rest_caller: RESTCaller,
                        ) -> tuple[int, dict]:
        
        is_lasttime = False
        if not configure.get('C_DEPOSIT_BALANCE'):
           configure['C_DEPOSIT_BALANCE'] = configure['C_DEPOSIT_AMOUNT']

        if configure['C_DEPOSIT_BALANCE'] - configure['C_BET_AMOUNT'] <= 0:
            is_lasttime = True
            bet_amount = configure['C_DEPOSIT_BALANCE']
        else:
            bet_amount = configure['C_BET_AMOUNT']

        deposit_balance = configure['C_DEPOSIT_BALANCE'] - bet_amount
        bet_seq = configure['C_BET_SEQ'] + 1
        
        param = dict(
            game_id = configure.get('C_GAME_ID'),
            account_id = configure.get('C_ACCOUNT_ID'),
            bet_seq = bet_seq,
            bet_amount = bet_amount,
            deposit_balance = deposit_balance,
            deposit_amount  = configure['C_DEPOSIT_AMOUNT'],
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

            if is_lasttime:
                from miniagent import scheduler
                scheduler.remove_job(initial_param['job_id'])

        return rtn, results