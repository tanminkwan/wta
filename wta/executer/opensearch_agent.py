from miniagent import configure
from miniagent.executer import ExecuterInterface
from miniagent.adapters.opensearch_caller import OpensearchCaller

url = "http://"+configure.get('ELASTIC_SEARCH_DOMAIN_NAME')\
            +":"+configure.get('ELASTIC_SEARCH_PORT')

class Query(ExecuterInterface):

    def _parcer(self, response):

        if not response['hits']['hits']:
            return {"results":[]}

        results = []
        
        for q in response['hits']['hits']:
            results.append(q['_source'])

        return {"results":results}

    def execute_command(self, 
                            initial_param: dict,
                            os_caller: OpensearchCaller,
                        ) -> tuple[int, dict]:
        
        index = initial_param['index']
        query =\
        {
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "game_id": initial_param['game_id']
                            }
                        }
                    ]
                }
            }
        }

        if initial_param.get('filter_conditions'):
                    
            for q in initial_param['filter_conditions']:

                query['query']['bool']['must'].append({"match": q})
        
        if initial_param.get('sort_condition'):

            query.update(dict(
                sort = initial_param['sort_condition'])
            )

        if initial_param.get('size'):

            query.update(dict(
                size = initial_param['size'])
            )

        print("### query : ", query)

        return os_caller.call_get(url, index, query, self._parcer)

class Distinct(ExecuterInterface):

    def _parcer(self, response):

        q = response.get('aggregations').get('unique_names').get('buckets')
        
        qq = [ row['key'] for row in q ]

        return {"accounts":qq}

    def execute_command(self, 
                            initial_param: dict,
                            os_caller: OpensearchCaller,
                        ) -> tuple[int, dict]:
        
        index = initial_param['index']
        query =\
        {
            "query": {
                "match": {
                    "game_id": initial_param['game_id']
                }
            },  
            "aggs":{
                "unique_names": {
                    "terms": {
                        "field": initial_param['dictinct_column']+".keyword"
                    }
                }
            },
            "_source": False
        }

        return os_caller.call_get(url, index, query, self._parcer)
