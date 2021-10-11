from xml.etree import ElementTree as ET
from .constants import Endpoints, Rootkeys, PRODUCTION, TOKEN_RE, DEVICE_RE
from . import api_models as model
from . import login
import requests
import re

import logging
logger = logging.getLogger("pss_api")

class ApiContainer:
	def __init__(self, response, full_service: str, *, r_params: dict = None):
		self.http_resp = response
		try:
			self.http_resp.raise_for_status()
		except Exception as e:
			logger.error(f'[RESP {self.http_resp.status_code}] Getting from API page failed.')
			raise e
		self.xml = None
		if self.http_resp.request.method == "POST":
			self.xml = ET.fromstring(self.http_resp.content.decode('utf-8'))
		else:
			self.xml = ET.fromstring(self.http_resp.text)
		self.endpoint = full_service
		self.r_params = r_params or None
		
	def to_model(self, only_one=False, last=False) -> model.Model:
		if last:
			only_one = True
		target_model = None

		if self.endpoint in [Endpoints.SEARCH_USER.value, Endpoints.ALLIANCE_USERS.value]:
			target_model = model.Player
		elif self.endpoint in [Endpoints.TOP_ALLIANCES.value, Endpoints.GET_ALLIANCE.value]:
			target_model = model.Alliance
		elif self.endpoint == Endpoints.GET_SPRITE.value:
			target_model = model.Sprite
		elif self.endpoint == Endpoints.GET_DIVISIONS.value:
			target_model = model.Division
		elif self.endpoint == Endpoints.SHIP_DESIGNS.value:
			target_model = model.ShipDesign
		elif self.endpoint == Endpoints.INSPECT_SHIP.value:
			target_model = model.InspectShipData
		elif self.endpoint == Endpoints.SEND_MESSAGE.value:
			target_model = model.Message
		else:
			target_model = model.Model
			print("Unknown!:", self.http_resp.text)

		if self.endpoint in Rootkeys.keys():
			index = ''
			if only_one:
				if last:
					index = '[last()]'
				else:
					index = '[1]'

			self.xml = self.xml.findall(f".//{Rootkeys[self.endpoint]}" + index)
			if len(self.xml) == 1:
				self.xml = self.xml[0]
		
		return model.return_model(target_model, self)


def get(service, endpoint: str = None, *, params: dict = {}, needs_token: bool = False):
	if needs_token:
		params["accessToken"] = login.generate_token()

	if isinstance(service, Endpoints):
		endpoint = service.value
	elif endpoint:
		endpoint = service + '/' + endpoint
	else:
		endpoint = service
	resp = requests.get(f"{PRODUCTION}/{endpoint}", params=params)
	logger.info(f'[GET {resp.status_code}] {endpoint} {params}')

	return ApiContainer(resp, endpoint, r_params=params)

def post(service, endpoint: str = None, *, params: dict = {}, token_info: str = None):
	# token info is token
	# token info is device key
	# token info is None - generate token
	token = None
	if token_info:
		if re.match(TOKEN_RE, token_info):
			token = token_info
		elif re.match(DEVICE_RE, token_info):
			token = login.from_device_key(token_info)
	else:
		token = login.generate_token()
	
	params['AccessToken'] = token

	if isinstance(service, Endpoints):
		endpoint = service.value
	elif endpoint:
		endpoint = service + '/' + endpoint
	else:
		endpoint = service

	resp = requests.post(f"{PRODUCTION}/{endpoint}", json=params)
	logger.info(f'[POST {resp.status_code}] {endpoint} {params}')

	return ApiContainer(resp, endpoint, r_params=params)