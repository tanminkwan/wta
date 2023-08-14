import os
from datetime import datetime, timedelta

#DEBUG
DEBUG = os.getenv("DEBUG", 'True').lower() in ('true', '1', 't')

#
COMMAND_RECEIVER_ENABLED = False
MESSAGE_RECEIVER_ENABLED = \
    os.environ.get('MESSAGE_RECEIVER_ENABLED', 'True').lower() in ('true', '1', 't')

import __main__
AGENT_NAME = os.environ.get('AGENT_NAME') or \
    os.path.basename(__main__.__file__).split('.')[0]

AGENT_ROLES = os.environ.get('AGENT_ROLES') or \
    os.path.basename(__main__.__file__).split('.')[0]

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

#Custom defined valuables
C_OPENAI_API_KEY = "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"

C_GAME_ID = os.environ.get('GAME_ID') or "test_game"
C_ACCOUNT_ID = os.environ.get('ACCOUNT_ID') or "test_account"
C_BET_SEQ = 0
C_DEPOSIT_BALANCE = 100000
C_BET_CYCLE_SEC = 20
C_BET_AMOUNT = 5000

C_SERVICE_ENDPOINT =\
{
    "openai_agent":OPENAI_AGENT_SERVICE_ADDRESS+"/api/v1",
    "betting_booth":BETTING_BOOTH_SERVICE_ADDRESS+"/api/v1",
    "k8s_agent":K8S_AGENT_SERVICE_ADDRESS+"/api/v1",
    "opensearch_agent":ELASTICSEARCH_AGENT_SERVICE_ADDRESS+"/api/v1",
    "game_manager":GAME_MANAGER_SERVICE_ADDRESS+"/api/v1",
    "game_panel":GAME_PANEL_SERVICE_ADDRESS+"/api/v1",
}

PREWORK =\
[
    {
        "executer":"wta.executer.calculator.Prework",
        "agent_roles":["calculator"],
    }
]

EXECUTERS_BY_TOPIC =\
[
    {"topic":"wta.raffle",
    "executer":"wta.executer.game_manager.Raffle",
    "agent_roles":["game_manager"]},
    {"topic":"wta.game.status",
    "executer":"wta.executer.service_manager.Status",
    "agent_roles":["service_manager"]},
    {"topic":"wta.deposit",
    "executer":"wta.executer.service_manager.Deposit",
    "agent_roles":["service_manager"]},
    {"topic":"wta.bet",
    "executer":"wta.executer.calculator.Bet",
    "agent_roles":["calculator"]},
    {"topic":"wta.calc.bet",
    "executer":"wta.executer.raffle.CalcBet",
    "agent_roles":["raffle"]},
]

#Scheduler
SCHEDULER_TIMEZONE = "Asia/Seoul" 
SCHEDULER_API_ENABLED = True
#EXIT_AFTER_JOBS = os.getenv("EXIT_AFTER_JOBS", 'false').lower() in ('true', '1', 't')
EXIT_AFTER_JOBS = True if AGENT_ROLES in ('betting_agent','fallbacj') else False
SCHEDULED_JOBS =\
[
    {
        "executer":"wta.executer.betting_agent.RequestBet",
        "trigger":"interval",
        "id":"request_bet",
        "name":"Request Bet",
        "seconds":C_BET_CYCLE_SEC,
        "params":{"bet_amount":C_BET_AMOUNT},
        "start_date":datetime.now()+timedelta(minutes=1),
        "end_date":datetime.now()+timedelta(minutes=5),
        "agent_roles":["betting_agent"],
    },
]
