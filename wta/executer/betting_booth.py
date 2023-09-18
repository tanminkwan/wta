from miniagent import configure
from miniagent.executer import ExecuterInterface
from miniagent.adapters.kafka_producer import KafkaProducerAdapter
from miniagent.common import now
import logging

class Bet(ExecuterInterface):

    def execute_command(self, 
                            initial_param: dict, 
                            producer: KafkaProducerAdapter,
                        ) -> tuple[int, dict]:
        
        topic = 'wta.bet'
        
        message = initial_param.copy()
        message.update({"bet_date":now().isoformat()})

        print("## message : ", message)
        rtn, result = producer.produce_message(
                        topic= topic,
                        message= message
                    )
        logging.warning("produce to wta.bet : ")
        logging.warning("rtn: "+str(rtn))
        logging.warning("result : "+str(result))
        
        return rtn, result