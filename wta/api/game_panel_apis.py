from flask import request, make_response, render_template, after_this_request
from miniagent import api, app, configure
from flask_restful import reqparse
from flask_api import status
from miniagent.executer import ExecuterCaller
from miniagent.event_receiver import Resource
from datetime import datetime, timedelta
from requests import get


@app.route('/api/v1/opensearch/<path:path>')
def proxy(path):

    print("### path : ", path)
    url = configure.get('C_SERVICE_ENDPOINT').get('opensearch_agent')    

    print("### url : ", f'http://{url}/opensearch/{path}')
    
    return get(f'http://{url}/opensearch/{path}').content

@app.route('/join_game')
def join_game_page():
    
    account_id = request.cookies.get('wts_game_account_id')
    expires = request.cookies.get('wts_game_account_id_expires')
    
    if not account_id:
        account_id = ""
    
    game_duration = configure['C_GAME_DURATION'] if configure.get('C_GAME_DURATION') else 300


    resp = make_response(render_template('join_game.html', account_id=account_id , game_duration = game_duration))
    
    return resp

@app.route('/monitor/<string:account_id>')
def monitor_page(account_id:str):

    print("## configure['C_GAME_START_DATE'] : ", configure['C_GAME_START_DATE'])
    game_start_date = configure['C_GAME_START_DATE'].isoformat()

    return render_template('monitor.html', \
            game_id=configure['C_GAME_ID'], account_id=account_id, game_start_date=game_start_date)

class Deposit(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('game_user_name', type=str)
    parser.add_argument('account_id', type=str)
    parser.add_argument('deposit_amount', type=int)
    #parser.add_argument('start_secs', type=int)
    #parser.add_argument('bet_cycle_secs', type=int)
    #parser.add_argument('bet_amount', type=int)
    parser.add_argument('bet_schedules', type=dict, action="append")

    def post(self):

        @after_this_request
        def set_cookie(response):
            #response.set_cookie('wts_game_account_id', uuid.uuid4().hex, max_age=300, httponly=True)
            response.set_cookie('wts_game_account_id', args['account_id'], max_age=timedelta(minutes=10), httponly=True)
            return response
        
        args = Deposit.parser.parse_args()

        print("### args", args)

        data = dict(
            initial_param = args,
            executer = 'wta.executer.game_panel.Deposit',
        )

        _, rtn_message = ExecuterCaller.instance().execute_command(data)

        return rtn_message, status.HTTP_200_OK

    post.permitted_roles = ["game_panel"]

api.add_resource(Deposit, '/game_panel/deposit', endpoint='deposit')