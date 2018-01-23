# Credentials Class

from keystoneauth1 import loading

class Credentials:
    def __init__(self, auth_url, project_id, user_domain_name, username, password):
        self._auth_url = auth_url
        self._project_id = project_id
        self._user_domain_name = user_domain_name
        self._username = username
        self._password = password

    def getAuth(self):
        loader = loading.get_plugin_loader('password')
        auth = loader.load_from_options(auth_url=self._auth_url,
                                        username=self._username,
                                        password=self._password,
                                        project_id=self._project_id,
                                        user_domain_name=self._user_domain_name)
        return auth
