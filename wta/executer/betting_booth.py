from miniagent import configure
from miniagent.executer import ExecuterInterface
from miniagent.adapters.kafka_producer import KafkaProducerAdapter

import uuid
from datetime import datetime

class Bet(ExecuterInterface):

    def execute_command(self, 
                            initial_param: dict, 
                            producer: KafkaProducerAdapter,
                        ) -> tuple[int, dict]:
        
        topic = 'wta.bet'
        now =  datetime.now()

        message = initial_param.copy()
        message.update({"bet_date":now.isoformat()})

        print("## message : ", message)

        return producer.produce_message(
            topic= topic,
            message= message
            )