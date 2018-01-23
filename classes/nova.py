# Nova Class

from keystoneauth1 import session
from novaclient import client
from datetime import datetime

class Nova:
    def __init__(self, credentials):
        sess = session.Session(auth=credentials.getAuth())
        self._client = client.Client(2, session=sess)

    def getServer(self, server_id):
        return self._client.servers.get(server_id)

    def getFlavor(self, flavor_id):
        return self._client.flavors.get(flavor_id)
