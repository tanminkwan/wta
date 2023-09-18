import requests
import uuid
import random
from time import sleep

for i in range(50):

    r = random.randrange(5, 15)
    bet_schedules = [{"waiting_secs": round((300/r)*j+10),"bet_amount":500} for j in range(r)]

    j_dict = dict(
        game_user_name = 'worker' + str(i),
        account_id = uuid.uuid4().hex[6:],
        deposit_amount = 500*r,
        bet_schedules = bet_schedules
    )

    sleep(2)
    print(str(i))
    r = requests.post('http://wta.leebalso.org/api/v1/game_panel/deposit', json=j_dict)