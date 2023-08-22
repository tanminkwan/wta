from flask import render_template
from miniagent import api, app
from flask_restful import reqparse
from flask_api import status
from miniagent.executer import ExecuterCaller
from miniagent.event_receiver import Resource

@app.route('/create_game')
def create_game_page():
    return render_template('create_game.html')


class Game(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('game_name', type=str)
    parser.add_argument('signup_date', type=str)
    parser.add_argument('start_date', type=str)
    parser.add_argument('raffle_rules', type=list, location='json')

    def post(self):

        args = Game.parser.parse_args()

        print("### game_name", args['game_name'])
        print("### signup_date", args['signup_date'])
        print("### start_date", args['start_date'])
        print("### raffle_rules", args['raffle_rules'])

        for rr in args['raffle_rules']:
            code = rr['code']

            if not code:
                return {'error':'code is empty','code':''}, \
                    status.HTTP_400_BAD_REQUEST
            
            funcs = {}
            try:
                exec(code, funcs)
                rs_f = funcs['f']
            except SyntaxError as e:
                print(e.__str__())
                return {'error':'code_syntax_error','code':code}, \
                    status.HTTP_400_BAD_REQUEST
            except NameError as e:
                print(e.__str__())
                return {'error':'name_error','code':code}, \
                    status.HTTP_400_BAD_REQUEST
            except KeyError as e:
                print(e.__str__())
                return {'error':'function_f_not_exists','code':code}, \
                    status.HTTP_400_BAD_REQUEST

        data = dict(
            initial_param = dict(
                game_name = args['game_name'],
                signup_date = args['signup_date'],
                start_date = args['start_date'],
                raffle_rules = args['raffle_rules'],
            ),
            executer = 'wta.executer.game_manager.Game',
        )

        _, rtn_message = ExecuterCaller.instance().execute_command(data)

        return rtn_message, status.HTTP_200_OK

    post.permitted_roles = ["game_manager"]

api.add_resource(Game, '/game_manager/game', endpoint='game')
