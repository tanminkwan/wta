from miniagent import configure

def _get_url(agent_name:str):
    return configure.get('C_SERVICE_ENDPOINT').get(agent_name)