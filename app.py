from miniagent import app, configure

if configure['RUN_TYPE']=='SERVICE':

    port=configure.get('PORT') or 5000
    debug=configure.get('DEBUG') or True

    app.run(host="0.0.0.0", port=port, use_reloader=False, debug=debug)

elif configure['RUN_TYPE']=='JOB':

    while True:
        pass

elif configure['RUN_TYPE']=='APP':

    pass
