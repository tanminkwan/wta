from miniagent import app, configure

run_type = configure['RUN_TYPE'].upper()

if run_type=='SERVICE':

    port=configure.get('PORT') or 5000
    debug=configure.get('DEBUG') or True

    app.run(host="0.0.0.0", port=port, use_reloader=False, debug=debug)

elif run_type=='JOB':

    while True:
        pass

elif run_type=='APP':

    pass
