import yaml
from pathlib import Path
import requests
from datetime import datetime
from pytz import timezone, UnknownTimeZoneError
from tzlocal import get_localzone

TIMEZONE = "Asia/Seoul" 

def local_dt_str(iso_str:any):
    try:
        if isinstance(iso_str, datetime):
            dt = iso_str
        else:
            dt = datetime.fromisoformat(iso_str)
        local_dt = timezone(TIMEZONE).localize(dt)
        local_dt_str = local_dt.isoformat()        
    except ValueError:
        return iso_str
    except UnknownTimeZoneError:
        return iso_str

    return local_dt_str

def now():
      
    try:
        now = datetime.now(timezone(TIMEZONE))
    except UnknownTimeZoneError:
        now = datetime.now()
    return now

n1 = datetime.now()
n2 = n1.isoformat()

print("n1 : ", n1)
print("n2 : ", n2)

print("n1 local_dt_str : ", local_dt_str(n1))
print("n2 local_dt_str : ", local_dt_str(n2))

t1 = "2023-09-07T23:03"
t2 = "2023-09-07T23:03:59.556368+09:00"
q1 = datetime.fromisoformat(t1)
q2 = datetime.fromisoformat(t2)
#m = (q2 - q1).total_seconds()
print(local_dt_str(t1))


"""
### create game_panel
file_name = './k8s/game_panel-deployment.yaml'

yaml_dict = yaml.safe_load(Path(file_name).read_text())
deployment_dict = {"deployment":yaml_dict}

url = "http://123.37.5.187/api/v1/k8s/deployments/wta"

response = requests.post(url, json=deployment_dict)

file_name = './k8s/game_panel-service.yaml'

yaml_dict = yaml.safe_load(Path(file_name).read_text())
service_dict = {"service":yaml_dict}

url = "http://123.37.5.187/api/v1/k8s/services/wta"

response = requests.post(url, json=service_dict)

### create calculator
file_name = './k8s/calculator-deployment.yaml'

yaml_dict = yaml.safe_load(Path(file_name).read_text())
deployment_dict = {"deployment":yaml_dict}

url = "http://123.37.5.187/api/v1/k8s/deployments/wta"

response = requests.post(url, json=deployment_dict)

### create raffle
file_name = './k8s/raffle-deployment.yaml'

yaml_dict = yaml.safe_load(Path(file_name).read_text())
deployment_dict = {"deployment":yaml_dict}

url = "http://123.37.5.187/api/v1/k8s/deployments/wta"

response = requests.post(url, json=deployment_dict)
url = "http://123.37.5.187/api/v1/k8s/deployment/wta/game-panel-v1"

response = requests.delete(url)

url = "http://123.37.5.187/api/v1/k8s/service/wta/game-panel"

response = requests.delete(url)

### create betting_agent
file_name = './k8s/betting_agent-job.yaml'

yaml_dict = yaml.safe_load(Path(file_name).read_text())
job_dict = {"job":yaml_dict}
bet_schedules = \
"[{'waiting_secs': 25, 'bet_amount': 5098}, {'waiting_secs': 50, 'bet_amount': 3609}, {'waiting_secs': 75, 'bet_amount': 2773}, {'waiting_secs': 100, 'bet_amount': 5098}, {'waiting_secs': 125, 'bet_amount': 2834}, {'waiting_secs': 150, 'bet_amount': 5098}, {'waiting_secs': 175, 'bet_amount': 5098}, {'waiting_secs': 200, 'bet_amount': 5098}, {'waiting_secs': 225, 'bet_amount': 5098}, {'waiting_secs': 250, 'bet_amount': 5098}, {'waiting_secs': 275, 'bet_amount': 5098}]"
job_name = 'betting-agent-12345678'

yaml_dict['metadata']['name'] = job_name
#yaml_dict['spec']['template']['metadata']['labels']['app'] = job_name
yaml_dict['spec']['template']['spec']['containers'][0]['name'] = job_name
message = job_dict['job']['spec']['template']['spec']['containers'][0]['env']

env_params = dict(
    bet_schedules = bet_schedules,
    game_id = 'aaabbb111',
    game_name = 'test',
    game_start_date = datetime.now().isoformat(),
    game_user_name = 'kim',
    account_id = 'aaasssddd11122233',
    deposit_amount = str(5400),
)

for item, value in list(env_params.items()):
    message.append(dict(
            name = item.upper(),
            value = str(value)
        ))
print(yaml_dict)

url = "http://123.37.6.71/api/v1/k8s/jobs/wta"

response = requests.post(url, json=job_dict)
print(job_dict)

url = "http://123.37.5.187/api/v1/k8s/job/wta/betting-agent-xxxx"
response = requests.delete(url)
"""

### create game_panel
file_name = './k8s/game_panel-deployment.yaml'

yaml_dict = yaml.safe_load(Path(file_name).read_text())
deployment_dict = {"deployment":yaml_dict}

url = "http://123.37.5.100/api/v1/k8s/deployments/wta"

response = requests.post(url, json=deployment_dict)

#print(deployment_dict)