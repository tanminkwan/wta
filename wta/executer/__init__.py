from miniagent import configure
from miniagent.adapters.rest_caller import RESTCaller
from .opensearch_agent import Query # If it is not declared, error may occure.

def _get_url(agent_name:str):
    return configure.get('C_SERVICE_ENDPOINT').get(agent_name)

def _get_game_info():
    url = "http://"+_get_url('config_map')+"/config_map"
    return RESTCaller().call_get(url=url)
