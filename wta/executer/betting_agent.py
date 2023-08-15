from miniagent import configure
from miniagent.executer import ExecuterInterface
from miniagent.adapters.rest_caller import RESTCaller
import logging

def _get_url(agent_name:str):
    return configure.get('C_SERVICE_ENDPOINT').get(agent_name)

class RequestBet(ExecuterInterface):

    def execute_command(self, 
                            initial_param: dict,
                            rest_caller: RESTCaller,
                        ) -> tuple[int, dict]:
        
        bet_seq = configure['C_BET_SEQ'] + 1

        is_lasttime = False
        if not configure.get('C_DEPOSIT_BALANCE'):
           configure['C_DEPOSIT_BALANCE'] = configure['C_DEPOSIT_AMOUNT']

        if configure['C_DEPOSIT_BALANCE'] - configure['C_BET_AMOUNT'] <= 0:
            is_lasttime = True

        if is_lasttime:
            bet_amount = configure['C_DEPOSIT_BALANCE']
        else:
            bet_amount = configure['C_BET_AMOUNT']

        deposit_balance = configure['C_DEPOSIT_BALANCE'] - bet_amount
        
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