import aiohttp
import json

# Bitcoin node client
class Bitcoin(object):
    def __init__(self, endpoint, rid="bitcoin-client"):
        self.endpoint = endpoint
        self.rid = rid

    def dead_response(self, message="Invalid Request"):
        return {"error": {
            "code": 404, "message": message
        }, "id": self.rid}

    def response(self, result, error=None):
        return {
            "error": error, "result": result,
            "id": self.rid
        }

    async def make_request(self, method, params=[]):
        async with aiohttp.ClientSession() as session:
            headers = {"content-type": "text/plain;"}
            data = json.dumps({
                "method": method, "params": params,
                "id": self.rid
            })

            try:
                async with session.post(self.endpoint, headers=headers, data=data) as response:
                    resp = await response.json()
                    return resp
            except Exception:
                return self.dead_response()