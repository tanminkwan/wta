from flask import render_template
from miniagent import api, app
from flask_restful import reqparse
from flask_api import status
from miniagent.executer import ExecuterCaller
from miniagent.event_receiver import Resource

@app.route('/join_game')
def join_game_page():
    return render_template('join_game.html')

@app.route('/monitor/<string:game_id>/<string:account_id>')
def monitor_page(game_id:str, account_id:str):
    return render_template('monitor.html', game_id=game_id, account_id=account_id)

class Deposit(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('game_user_name', type=str)
    parser.add_argument('account_id', type=str)
    parser.add_argument('deposit_amount', type=int)
    parser.add_argument('start_secs', type=int)
    parser.add_argument('bet_cycle_secs', type=int)
    parser.add_argument('bet_amount', type=int)

    def post(self):

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
