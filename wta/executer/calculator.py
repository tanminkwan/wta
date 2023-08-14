from miniagent import configure
from miniagent.executer import ExecuterInterface
from miniagent.adapters.rest_caller import RESTCaller
from . import _get_url

class Prework(ExecuterInterface):

    def execute_command(self, 
                            initial_param: dict,
                            rest_caller: RESTCaller,
                        ) -> tuple[int, dict]:
        
        url = "http://"+_get_url('opensearch_agent')\
                 +"/opensearch/latest_calc_bet/" + configure.get('C_GAME_ID')
        
        rtn, results = rest_caller.call_get(url=url)

        configure['C_TOTAL_ACCOUNT_COUNT'] = results.get('total_account_count')
        configure['C_TOTAL_BET_COUNT']     = results.get('total_bet_count')
        configure['C_TOTAL_BET_AMOUNT']    = results.get('total_bet_amount')
        configure['C_TOTAL_DEPOSIT_AMOUNT'] = results.get('total_deposit_amount')
        #results.get('total_deposit_balance')
        #results.get('average_bet_amount_per_account')
        #results.get('average_bet_amount_per_round')
        #results.get('average_deposit_balance_per_account')

        return rtn, results