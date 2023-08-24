from miniagent import app, configure

port=5013 #k8s_agent

app.run(host="0.0.0.0", port=port, use_reloader=False, debug=False)