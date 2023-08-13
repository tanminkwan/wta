from miniagent import configure
from miniagent.executer import ExecuterInterface
from ..adapter.openai_api_adapter import OpenAiApiCaller

class Prompt(ExecuterInterface):

    def execute_command(self, 
                            initial_param: dict, 
                            oai: OpenAiApiCaller,
                        ) -> tuple[int, dict]:
                
        prompt = initial_param.get('prompt')
        prompt['api_key'] = configure.get('C_OPENAI_API_KEY')
        
        return oai.get_response(prompt)