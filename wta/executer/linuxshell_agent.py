from miniagent import configure
from miniagent.executer import ExecuterInterface

import subprocess
import logging

class LaunchService(ExecuterInterface):
    
    def execute_command(self, 
                            initial_param: dict,
                        ) -> tuple[int, dict]:

        if not initial_param.get('service'):
            return -1, {'message':'Service is not in initial_param.'}
        
        print("## LaunchService : ", initial_param )
        service = initial_param['service']
        
        env_str = ""
        if initial_param.get('env_params'):
            for item, value in list(initial_param['env_params'].items()):
                env_str += "export "+item.upper()+"="+str(value)+";"

        subprocess.run(["bash","-c",env_str+"python3 "+service+".py &"], stdout=subprocess.DEVNULL)

        message = service + ' is launched.'
        return 1, {'message':message}