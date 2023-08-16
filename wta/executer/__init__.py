from miniagent import configure

def _get_url(agent_name:str):
    return configure.get('C_SERVICE_ENDPOINT').get(agent_name)

for rr in configure['C_RAFFLE_RULES']:

    funcs = {}
    exec(rr['code'], funcs)
    f = funcs['f']

    rr['function'] = f