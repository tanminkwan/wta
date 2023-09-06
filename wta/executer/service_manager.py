from miniagent import configure
from miniagent.executer import ExecuterInterface
from miniagent.adapters.rest_caller import RESTCaller
from miniagent.adapters.kafka_producer import KafkaProducerAdapter
import logging
import yaml
from pathlib import Path

from datetime import datetime
from . import _get_url, _get_game_info

def _create_k8s_job(rest_caller, launch_info):

    url = "http://"+_get_url('k8s_agent')+"/k8s/jobs/wta"

    file_name = './k8s/'+launch_info['service']+'-job.yaml'

    yaml_dict = yaml.safe_load(Path(file_name).read_text())
    job_dict = {"job":yaml_dict}

    try:
        rtn, result = rest_caller.call_post(
                            url=url, 
                            json=job_dict
                        )
    except Exception as e:
        message = "Exception : " + e.__str__()
        logging.error(message)
        return -1, {"error":message}
            
    if rtn == 200:
        return 1, result
    else:
        return -1, {"error":result}

def _create_k8s_deployment(rest_caller, launch_info):

    url = "http://"+_get_url('k8s_agent')+"/k8s/deployments/wta"

    file_name = './k8s/'+launch_info['service']+'-deployment.yaml'

    yaml_dict = yaml.safe_load(Path(file_name).read_text())
    deployment_dict = {"deployment":yaml_dict}

    try:
        rtn, result = rest_caller.call_post(
                            url=url, 
                            json=deployment_dict
                        )
    except Exception as e:
        message = "Exception : " + e.__str__()
        logging.error(message)
        return -1, {"error":message}
            
    if rtn == 200:
        return 1, result
    else:
        return -1, {"error":result}

def _create_k8s_service(rest_caller, launch_info):

    url = "http://"+_get_url('k8s_agent')+"/k8s/services/wta"

    file_name = './k8s/'+launch_info['service']+'-service.yaml'

    yaml_dict = yaml.safe_load(Path(file_name).read_text())
    service_dict = {"service":yaml_dict}

    try:
        rtn, result = rest_caller.call_post(
                            url=url, 
                            json=service_dict
                        )
    except Exception as e:
        message = "Exception : " + e.__str__()
        logging.error(message)
        return -1, {"error":message}
            
    if rtn == 200:
        return 1, result
    else:
        return -1, {"error":result}

def _create_service(rest_caller, launch_info):

    url = "http://"+_get_url('k8s_agent')+"/launch"

    try:
        rtn, result = rest_caller.call_post(
                            url=url, 
                            json=launch_info
                        )
    except Exception as e:
        message = "Exception : " + e.__str__()
        logging.error(message)
        return -1, {"error":message}
            
    if rtn == 200:
        return 1, result
    else:
        return -1, {"error":result}
    
def _kill_service(rest_caller, service):

    url = "http://"+_get_url('k8s_agent')+"/kill"

    try:
        rtn, result = rest_caller.call_post(
                            url=url, 
                            json={"service":service}
                        )
    except Exception as e:
        message = "Exception : " + e.__str__()
        logging.error(message)
        return -1, {"error":message}
            
    if rtn == 200:
        return 1, result
    else:
        return -1, {"error":result}

class Prework(ExecuterInterface):

    def execute_command(self, 
                            initial_param: dict,
                        ) -> tuple[int, dict]:
        
        configure['C_GAME_ID'] = None
        configure['C_GAME_NAME'] = None
        configure['C_GAME_START_DATE'] = None

        rtn, game_info = _get_game_info()

        if rtn==200:

            configure['C_GAME_ID'] = game_info['game_id']
            configure['C_GAME_NAME'] = game_info['game_name']
            configure['C_GAME_START_DATE'] = \
                datetime.strptime(game_info['start_date'], "%Y-%m-%dT%H:%M")
            
            print("## C_GAME_ID : ", configure['C_GAME_ID'])
            print("## C_GAME_NAME : ", configure['C_GAME_NAME'])
            
        elif rtn == 204:
            logging.warning("There is no game.")
        else:
            logging.error("_get_game_info error. rtn : " + str(rtn))
            return -1, {}

        return 1, {} 

class Status(ExecuterInterface):

    def _set_env_params(self, service):

        _params = dict(
            agent_name = service ,
            agent_roles = service ,
            run_type = 'app' if service == 'fallback' else 'service'
        )       

        return _params

    def execute_command(self, 
                            initial_param: dict,
                            rest_caller: RESTCaller,
                        ) -> tuple[int, dict]:

        rtn, game_info = _get_game_info()

        if rtn!=200:
            logging.error("_get_game_info error. rtn : " + str(rtn))
            return -1, {}

        if initial_param.get('game_id') != game_info['game_id']:
            return 0, {'message':'Game Id is wrong.'}

        configure['C_GAME_ID'] = game_info['game_id']
        configure['C_GAME_NAME'] = game_info['game_name']
        configure['C_GAME_START_DATE'] = \
                datetime.strptime(game_info['start_date'], "%Y-%m-%dT%H:%M")

        if initial_param['game_status'] == 'signup':

            services_to_creat = ['raffle', 'calculator', 'game_panel']

            for service in services_to_creat:

                launch_info = dict(
                    service = service,
                    env_params = self._set_env_params(service)
                )

                if configure['PLATFORM_TYPE']=='k8s':
                    rtn, result = _create_k8s_deployment(rest_caller, launch_info)
                    if  service == 'game_panel':
                        rtn, result = _create_k8s_service(rest_caller, launch_info)
                else:
                    rtn, result = _create_service(rest_caller, launch_info)

        elif initial_param['game_status'] == 'end':

            services_to_kill = ['raffle', 'calculator', 'game_panel']

            for service in services_to_kill:

                rtn, result = _kill_service(rest_caller, service)

            launch_info = dict(
                    service = 'fallback',
                    env_params = self._set_env_params('fallback')
                )

            if configure['PLATFORM_TYPE']=='k8s':
                rtn, result = _create_k8s_job(rest_caller, launch_info)
            else:
                rtn, result = _create_service(rest_caller, launch_info)

        return 1, {} 

class Deposit(ExecuterInterface):

    def execute_command(self, 
                            initial_param: dict,
                            rest_caller: RESTCaller,
                        ) -> tuple[int, dict]:        

        if initial_param.get('game_id') != configure.get('C_GAME_ID'):
            return 0, {'message':'Game Id is wrong.'}
        
        env_params = initial_param.copy()

        service = 'betting_agent'
        env_params.update(
            agent_name='betting_agent.'+env_params['account_id'],
            agent_roles='betting_agent',
            run_type = 'job',
            game_start_date = configure['C_GAME_START_DATE'].isoformat(),
        )

        launch_info = dict(
            service = service,
            env_params = env_params
        )

        if configure['PLATFORM_TYPE']=='k8s':
            rtn, result = _create_k8s_job(rest_caller, launch_info)
        else:
            rtn, result = _create_service(rest_caller, launch_info)
        
        return rtn, result