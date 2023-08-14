from miniagent import configure
from miniagent.executer import ExecuterInterface
from miniagent.adapters.rest_caller import RESTCaller

def _get_url(agent_name:str):
    return configure.get('C_SERVICE_ENDPOINT').get(agent_name)

class RequestBet(ExecuterInterface):

    def execute_command(self, 
                            initial_param: dict,
                            rest_caller: RESTCaller,
                        ) -> tuple[int, dict]:
        
        configure['C_BET_SEQ'] += 1
        configure['C_DEPOSIT_BALANCE'] -= configure['C_BET_AMOUNT']
        
        param = dict(
            game_id = configure.get('C_GAME_ID'),
            account_id = configure.get('C_ACCOUNT_ID'),
            bet_seq = configure.get('C_BET_SEQ'),
            bet_amount = configure.get('C_BET_AMOUNT'),
            deposit_balance = configure.get('C_DEPOSIT_BALANCE'),              
        )

        print("### param : ", param)
        url = "http://"+_get_url('betting_booth')\
                 +"/betting_booth"
        
        return rest_caller.call_post(
                    url=url, 
                    json={"bet":param}
                )