from miniagent import configure
from miniagent.executer import ExecuterInterface
from miniagent.adapters.kafka_producer import KafkaProducerAdapter
from miniagent.common import now

class Bet(ExecuterInterface):

    def execute_command(self, 
                            initial_param: dict, 
                            producer: KafkaProducerAdapter,
                        ) -> tuple[int, dict]:
        
        topic = 'wta.bet'
        
        message = initial_param.copy()
        message.update({"bet_date":now().isoformat()})

        print("## message : ", message)

        return producer.produce_message(
            topic= topic,
            message= message
            )