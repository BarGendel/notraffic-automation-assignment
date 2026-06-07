from playwright.sync_api import APIRequestContext, APIResponse


class NearMissApi:
    def __init__(self, request: APIRequestContext):
        self.request = request

    def get_by_signal(self, signal_id: str) -> APIResponse:
        return self.request.get(f"/data/near-miss.json?signalId={signal_id}")

    def get_json_by_signal(self, signal_id: str) -> dict:
        response = self.get_by_signal(signal_id)
        assert response.status == 200
        return response.json()
