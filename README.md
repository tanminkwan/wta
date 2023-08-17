# wta
Winner takes all Game

## Download banking-poc repository
```
$ get clone https://github.com/tanminkwan/wta.git
```
## Execute docker compose files
```
$ docker compose -f docker-compose-kafka.yml -f docker-compose-opensearch.yml -f docker-compose-zipkin.yml -f docker-compose.yml up -d
```
## Check all 12 containers
```
$ docker ps -a

IMAGE                                        PORTS              NAMES
tanminkwan/wta                                    client-clyde
tanminkwan/wta                                    client-bonnie
tanminkwan/wta                                    client-john_dillinger
tanminkwan/wta                                    banking-raffle
tanminkwan/wta                 0.0.0.0:8382->5000 banking-deposit
tanminkwan/wta                 0.0.0.0:8381->5000 banking-event
wurstmeister/zookeeper                       0.0.0.0:2181->2181 zookeeper
wurstmeister/kafka                           0.0.0.0:9092->9092 kafka
tanminkwan/cp-kafka-connect-added            0.0.0.0:8083->8083 banking-poc-kafka-connect-1
opensearchproject/opensearch                 0.0.0.0:9200->9200 opensearch
tanminkwan/opensearch-dashboards-no-security 0.0.0.0:5601->5601 opensearch-dashboards
openzipkin/zipkin                            0.0.0.0:9411->9411 zipkin
```
## Run kafka opensearch sink connector
```
echo '{"name":"opensearch-sink",
"config":{
"connector.class":"io.aiven.kafka.connect.opensearch.OpensearchSinkConnector",
"tasks.max":3,
"topics":"wta.game.status,wta.bet,wta.calc.bet,wta.raffle,wta.deposit,wta.fallback",
"key.ignore":"true",
"connection.url":"http://172.17.0.1:9200",
"type.name":"log",
"schema.ignore":"true"
}
}'|curl -X POST -d @- http://localhost:8083/connectors --header "content-Type:application/json"
```

## Open Zipkin web site and check the transactions

1. Clyde and Bonnie send requests to Deposit and Event every 2 minites. 
2. Deposit produces messages and Raffle consumes the messages via Kafka. 
3. Event calls Raffle whenever it receive a request from Clyde and Bonnie. 
4. John Dillinger requests deposit amount by account from Event every 4 minutes. 
5. Event retrieves this information from Opensearch and provides it to John Dillinger. 

You can see all of them on the Zipkin dashboard.(Maybe http://localhost:9411)