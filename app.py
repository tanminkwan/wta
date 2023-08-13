from miniagent import app, configure

port=configure.get('PORT') or 5000
debug=configure.get('DEBUG') or True

app.run(host="0.0.0.0", port=port, use_reloader=False, debug=debug)
