from miniagent import configure
from miniagent.executer import ExecuterInterface
from miniagent.adapters.opensearch_caller import OpensearchCaller

class LatestCalcBet(ExecuterInterface):

    def _parcer(self, response):
        q = response.get('aggregations').get('deposit_account_grp').get('buckets')
        
        qq = [ {
            "account":row['key'], 
            "count":row['doc_count'], 
            "amount_sum":row['amount_sum']['value']
            } for row in q]

        return {"results":qq}

    def execute_command(self, 
                            initial_param: dict,
                            os_caller: OpensearchCaller,
                        ) -> tuple[int, dict]:
        
        url = "http://"+configure.get('ELASTIC_SEARCH_DOMAIN_NAME')\
            +":"+configure.get('ELASTIC_SEARCH_PORT')
        
        index = 'deposit.raffle'
        query =\
        {
            "query": {
                "match_all": {}
            },
            "size": 1,
            "aggs": {
                "deposit_account_grp": {
                "terms": {
                    "field": "account.keyword"
                },
                "aggs": {
                    "amount_sum": {
                    "sum": {
                        "field": "amount"
                    }
                    }
                }
                }
            }
        }

        return os_caller.call_get(url, index, query, self._parcer)
