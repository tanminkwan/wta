from flask import make_response, render_template
from miniagent import api, app, configure

@app.route('/nogame')
def nogame_page():
    
    return make_response(render_template('nogame.html'))

@app.route('/site-qrcode')
def site_qrcode_page():

    return make_response(render_template('site_qrcode.html'))