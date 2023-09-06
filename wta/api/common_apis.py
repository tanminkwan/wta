from flask_api import status
from miniagent import api
from miniagent.event_receiver import Resource

# API for k8s livenessProbe
class Status(Resource):

    def get(self):

        return {"message":"I'm alive.."}, status.HTTP_200_OK

api.add_resource(Status, '/status', endpoint='status')
