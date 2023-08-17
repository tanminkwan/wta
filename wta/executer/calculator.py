from miniagent import configure
from miniagent.executer import ExecuterInterface
from miniagent.adapters.rest_caller import RESTCaller
from miniagent.adapters.kafka_producer import KafkaProducerAdapter

from datetime import datetime
from . import _get_url

class Prework(ExecuterInterface):

    def execute_command(self, 
                            initial_param: dict,
                            rest_caller: RESTCaller,
                        ) -> tuple[int, dict]:
        
        url = "http://"+_get_url('opensearch_agent')\
                 +"/opensearch/latest_calc_bet/" + configure.get('C_GAME_ID')
        
        rtn, result = rest_caller.call_get(url=url)

        tot = {}

        print("call opensearch :", rtn, result)
        if rtn == 200 and result.get('account'):
            tot['accounts']       = result.get('accounts') 
            tot['tot_bet_count']      = result.get('tot_bet_count')
            tot['tot_bet_amount']     = result.get('tot_bet_amount')
            tot['tot_deposit_amount'] = result.get('tot_deposit_amount')
        else:
            tot['accounts']           = set()
            tot['tot_bet_count']      = 0
            tot['tot_bet_amount']     = 0
            tot['tot_deposit_amount'] = 0

        tot['account_count']          = len(tot['accounts'])
        tot['tot_deposit_balance']    = tot['tot_deposit_amount'] - tot['tot_bet_amount']
            
        tot['avg_bet_amount_per_account'] = round(tot['tot_bet_amount']/tot['account_count']) \
                if tot['account_count']!=0 else 0
        tot['avg_bet_amount_per_round']   = round(tot['tot_bet_amount']/tot['tot_bet_count'])\
                if tot['tot_bet_count']!=0 else 0
        tot['avg_deposit_amount_per_account'] = \
                round(tot['tot_deposit_amount']/tot['account_count'])\
                if tot['account_count']!=0 else 0

        configure['C_STAT'] = tot

        result.update(tot)

        return rtn, result
    
class Calculator(ExecuterInterface):

    def execute_command(self, 
                            initial_param: dict,
                            producer: KafkaProducerAdapter,
                        ) -> tuple[int, dict]:
        
        topic = 'wta.calc.bet'
        print("## initial_param : ", initial_param)

        message = self._calculate_tot(initial_param.copy())
        
        print("## message : ", message)

        return producer.produce_message(
            topic= topic,
            message= message
            )
    
    def _calculate_tot(self, bet:dict) -> dict:
        
        stat = configure['C_STAT']
               
        now =  datetime.now()

        if bet['account_id'] not in stat['accounts']:
            stat['tot_deposit_amount']  += bet['deposit_amount']
            stat['tot_deposit_balance'] += bet['deposit_amount']

        stat['accounts'].add(bet['account_id'])
        stat['tot_bet_count']       += 1
        stat['tot_bet_amount']      += bet['bet_amount']
        stat['tot_deposit_balance'] -= bet['bet_amount']

        calculated_dict = dict(
            calc_date           = now.isoformat() ,
            account_count       = len(stat['accounts']) ,
            tot_bet_count       = stat['tot_bet_count'] ,
            tot_bet_amount      = stat['tot_bet_amount'] ,
            tot_deposit_amount  = stat['tot_deposit_amount'] ,
            tot_deposit_balance = stat['tot_deposit_balance'] ,
            avg_bet_amount_per_account = \
                round(stat['tot_bet_amount']/len(stat['accounts'])) ,
            avg_bet_amount_per_round = \
                round(stat['tot_bet_amount']/stat['tot_bet_count']) ,
            avg_deposit_amount_per_account = \
                round(stat['tot_deposit_amount']/len(stat['accounts'])) ,
        )

        calculated_dict.update(bet)

        return calculated_dict