import json
import requests

class Infura:
    def __init__(self, project_id, project_secret):
        self.url = "https://{}:{}@filecoin.infura.io".format(project_id, project_secret)

    def api_call(self, method, params=[]):
        headers = {'Content-Type': "application/json"}
        data = {"id": 1, "jsonrpc": "2.0", "method": method, "params": params}
        try:
            rtn = requests.post(self.url, headers=headers, data=json.dumps(data))
        except Exception as e:
            print("API Exception : {} ".format(str()))
            return {}

        return rtn.json()
