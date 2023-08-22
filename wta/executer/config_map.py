from miniagent import configure
from miniagent.executer import ExecuterInterface

class ConfigMap(ExecuterInterface):

    def execute_command(self, 
                            initial_param: dict,
                        ) -> tuple[int, dict]:
        
        if initial_param:
            configure['C_CONFIG_MAP'] = initial_param
        
        rtn, result = (1, configure['C_CONFIG_MAP']) if configure.get('C_CONFIG_MAP') else (0,{})

        print("### config map : ", configure.get('C_CONFIG_MAP'))
        
        return rtn, result