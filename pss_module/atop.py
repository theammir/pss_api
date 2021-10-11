from . import request
from .constants import Endpoints
from . import api_models as model

class Session:
	def __init__(self, token):
		self.token = token

	def send_message(self, text: str, channel: str):
		container = request.post(Endpoints.SEND_MESSAGE, params={'Message': text, 'ChannelKey': channel}, token_info=self.token)

		return container.to_model()

def search_users(search_string: str, *, only_one=False, last=False):
	container = request.get(Endpoints.SEARCH_USER, params={'searchString': search_string})

	return container.to_model(only_one, last)

get_users = search_users

def fleet_users(id: int, take: int = 1, skip: int = 0, *, only_one=False, last=False):
	if take == 1 or only_one:
		take = 1
		only_one = True
	container = request.get(Endpoints.ALLIANCE_USERS, params={'allianceId': id, 'take': take, 'skip': skip})

	return container.to_model(only_one=only_one, last=last)

alliance_users = fleet_users

def get_top_fleets(take: int, skip: int = 0, *, only_one=False, last=False):
	container = request.get(Endpoints.TOP_ALLIANCES, params={"take": take, "skip": skip})

	return container.to_model(only_one, last)

get_top_alliances = get_top_fleets

def get_settings(language_key: str, device_type: str = "DeviceTypeAndroid", *, only_one=False, last=False):
	container = request.get(Endpoints.GET_VERSION, params={'languageKey': language_key, "deviceType": device_type})

	return container.to_model(only_one, last)

def get_division_designs(*, only_one=False, last=False):
	container = request.get(Endpoints.GET_DIVISIONS)

	return container.to_model(only_one, last)

def search_fleets(name: str, take: int = 1, skip: int = 0, *, only_one=False, last=False):
	if take == 1 or only_one:
		only_one = True
		take = 1
	container = request.get(Endpoints.GET_ALLIANCE, params={'name': name, 'take': take, 'skip': skip}, needs_token=True)

	return container.to_model(only_one, last)

search_alliances = search_fleets

def inspect_ship(ship):
	if isinstance(ship, str):
		ship = search_users(ship, only_one=True).id
	if isinstance(ship, model.Player):
		ship = ship.id

	container = request.get(Endpoints.INSPECT_SHIP, params={'userId': ship}, needs_token=True)

	return container.to_model()

def send_message(text: str, channel: str, token_info: str):
	container = request.post(Endpoints.SEND_MESSAGE, params={'Message': text, 'ChannelKey': channel}, token_info=token_info)

	return container.to_model()