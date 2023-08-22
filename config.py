import os
from datetime import datetime, timedelta
from random import randrange

#DEBUG
DEBUG = os.getenv("DEBUG", 'True').lower() in ('true', '1', 't')

#
COMMAND_RECEIVER_ENABLED = False
MESSAGE_RECEIVER_ENABLED = \
    os.environ.get('MESSAGE_RECEIVER_ENABLED', 'True').lower() in ('true', '1', 't')

import __main__
AGENT_NAME = os.environ.get('AGENT_NAME') or \
    os.path.basename(__main__.__file__).rsplit('.',1)[0]

AGENT_ROLES = os.environ.get('AGENT_ROLES') or AGENT_NAME.split('.')[0]

#Infra hosts
ZIPKIN_DOMAIN_NAME = os.environ.get('ZIPKIN_DOMAIN_NAME') or 'localhost'
ZIPKIN_PORT =  os.environ.get('ZIPKIN_PORT') or '9411'
ZIPKIN_ADDRESS = (ZIPKIN_DOMAIN_NAME,int(ZIPKIN_PORT))
KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS') or 'localhost:9092'
KAFKA_BOOTSTRAP_SERVERS = KAFKA_BOOTSTRAP_SERVERS.split(',')
ELASTIC_SEARCH_DOMAIN_NAME = os.environ.get('ELASTIC_SEARCH_DOMAIN_NAME') or 'localhost'
ELASTIC_SEARCH_PORT = os.environ.get('ELASTIC_SEARCH_PORT') or '9200'

print("MESSAGE_RECEIVER_ENABLED : ", MESSAGE_RECEIVER_ENABLED)
print("AGENT_NAME : ", AGENT_NAME)
print("AGENT_ROLES : ", AGENT_ROLES)

CUSTOM_APIS_PATH = "wta.api"

#wts services
OPENAI_AGENT_SERVICE_ADDRESS  = \
    os.environ.get('OPENAI_AGENT_SERVICE_ADDRESS') or 'localhost:5011'
BETTING_BOOTH_SERVICE_ADDRESS = \
    os.environ.get('BETTING_BOOTH_SERVICE_ADDRESS') or 'localhost:5012'
K8S_AGENT_SERVICE_ADDRESS     = \
    os.environ.get('OPENAI_AGENT_SERVICE_ADDRESS') or 'localhost:5013'
ELASTICSEARCH_AGENT_SERVICE_ADDRESS = \
    os.environ.get('ELASTICSEARCH_AGENT_SERVICE_ADDRESS') or 'localhost:5014'
GAME_MANAGER_SERVICE_ADDRESS = \
    os.environ.get('GAME_MANAGER_SERVICE_ADDRESS') or 'localhost:5015'
GAME_PANEL_SERVICE_ADDRESS = \
    os.environ.get('GAME_PANEL_SERVICE_ADDRESS') or 'localhost:5016'
CONFIG_MAP_SERVICE_ADDRESS = \
    os.environ.get('CONFIG_MAP_SERVICE_ADDRESS') or 'localhost:5017'

#Custom defined valuables
C_OPENAI_API_KEY = "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"

#C_GAME_ID = os.environ.get('GAME_ID') or "ec20fee9e8ee42dd92afaca3a89feafd"
#C_GAME_NAME = os.environ.get('GAME_NAME') or "test_game7"
C_ACCOUNT_ID = os.environ.get('ACCOUNT_ID') or AGENT_NAME
C_GAME_USER_NAME = os.environ.get('ACCOUNT_ID') or AGENT_NAME + '_형기'
C_BET_SEQ = 0
C_DEPOSIT_AMOUNT = int(os.environ.get('C_DEPOSIT_AMOUNT', str(53000)))
C_BET_CYCLE_SEC = int(os.environ.get('C_BET_CYCLE_SEC', str(randrange(20, 60, 10))))
C_BET_AMOUNT = int(os.environ.get('C_BET_AMOUNT', str(randrange(3000, 10000, 1000))))
C_START_SECS = int(os.environ.get('C_START_SECS', '30'))

_str_raffle_rule_comon = \
"""
def f( bet_seq:int=0, 
       bet_amount:int=0, 
       deposit_amount:int=0, 
       deposit_balance:int=0, 
       tot_deposit_amount:int=0,
       tot_deposit_balance:int=0, 
       avg_bet_amount_per_account:int=0, 
       avg_bet_amount_per_round:int=0, 
       tot_bet_amount:int=0, 
       tot_bet_count:int=0, 
       avg_deposit_amount_per_account:int=0, 
       account_count:int=0):
"""
_str_raffle_rule_1 = \
_str_raffle_rule_comon + \
"""
    if tot_bet_amount/tot_deposit_amount > 0.9:
        return True
    return False
"""
_str_raffle_rule_2 = \
_str_raffle_rule_comon + \
"""
    if deposit_balance == 0:
        return True
    return False
"""
_str_raffle_rule_3 = \
_str_raffle_rule_comon + \
"""
    if tot_deposit_balance <= 0:
        return True
    return False
"""

"""
C_RAFFLE_RULES = os.environ.get('RAFFLE_RULES') or \
[
    {"rule_name":"winner",
     "code":_str_raffle_rule_1,
     "winning_type":"percentage",
     "winning_point":50,
     "winner_count":1,
     "remaining_winner_count":1},
    {"rule_name":"fast_bettor",
     "code":_str_raffle_rule_2,
     "winning_type":"quantity",
     "winning_point":50000,
     "winner_count":2,
     "remaining_winner_count":2},
    {"rule_name":"no_more_diposit",
     "code":_str_raffle_rule_3,
     "winning_type":"quantity",
     "winning_point":0,
     "winner_count":1,
     "remaining_winner_count":1,
     "end_immediately":True},
]
"""
C_SERVICE_ENDPOINT =\
{
    "openai_agent":OPENAI_AGENT_SERVICE_ADDRESS+"/api/v1",
    "betting_booth":BETTING_BOOTH_SERVICE_ADDRESS+"/api/v1",
    "k8s_agent":K8S_AGENT_SERVICE_ADDRESS+"/api/v1",
    "opensearch_agent":ELASTICSEARCH_AGENT_SERVICE_ADDRESS+"/api/v1",
    "game_manager":GAME_MANAGER_SERVICE_ADDRESS+"/api/v1",
    "game_panel":GAME_PANEL_SERVICE_ADDRESS+"/api/v1",
    "config_map":CONFIG_MAP_SERVICE_ADDRESS+"/api/v1",
}

PREWORK =\
[
    {
        "executer":"wta.executer.calculator.Prework",
        "agent_roles":["calculator"],
    },
    {
        "executer":"wta.executer.raffle.Prework",
        "agent_roles":["raffle"],
    },
    {
        "executer":"wta.executer.betting_agent.Prework",
        "agent_roles":["betting_agent"],
    },
]

EXECUTERS_BY_TOPIC =\
[
    {"topic":"wta.raffle",
    "executer":"wta.executer.game_manager.End",
    "agent_roles":["game_manager"]},
    {"topic":"wta.game.status",
    "executer":"wta.executer.service_manager.Status",
    "agent_roles":["service_manager"]},
    {"topic":"wta.deposit",
    "executer":"wta.executer.service_manager.Deposit",
    "agent_roles":["service_manager"]},
    {"topic":"wta.bet",
    "executer":"wta.executer.calculator.Calculator",
    "agent_roles":["calculator"]},
    {"topic":"wta.calc.bet",
    "executer":"wta.executer.raffle.Raffle",
    "agent_roles":["raffle"]},
]

#Scheduler
SCHEDULER_TIMEZONE = "Asia/Seoul" 
SCHEDULER_API_ENABLED = True
#EXIT_AFTER_JOBS = os.getenv("EXIT_AFTER_JOBS", 'false').lower() in ('true', '1', 't')
EXIT_AFTER_JOBS = True if AGENT_ROLES in ('betting_agent','fallback') else False
SCHEDULED_JOBS =\
[
    {
        "executer":"wta.executer.betting_agent.RequestBet",
        "trigger":"interval",
        "id":"request_bet",
        "name":"Request Bet",
        "seconds":C_BET_CYCLE_SEC,
        "params":{"bet_amount":C_BET_AMOUNT},
        "start_date":datetime.now()+timedelta(seconds=C_START_SECS),
        "agent_roles":["betting_agent"],
    },
]
# job list : /scheduler/jobs