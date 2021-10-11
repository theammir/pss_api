import enum
import xml.etree.ElementTree as ET
import requests

class Endpoints(enum.Enum):
	SEARCH_USER  = 'UserService/SearchUsers'
	USER_LOGIN = 'UserService/DeviceLogin8'
	TOP_ALLIANCES = 'AllianceService/ListAlliancesByRanking'
	GET_ALLIANCE = 'AllianceService/SearchAlliances'
	ALLIANCE_USERS = 'AllianceService/ListUsers'
	INSPECT_SHIP = 'ShipService/InspectShip2'
	SHIP_DESIGNS = 'ShipService/ListAllShipDesigns2'
	LIST_LEAGUES  = 'LeagueService/ListLeagues2'
	GET_SPRITE = 'FileService/DownloadSprite'
	GET_VERSION = 'SettingService/GetLatestVersion3'
	GET_DIVISIONS = 'DivisionService/ListAllDivisionDesigns2'
	SEND_MESSAGE = 'MessageService/SendMessage3'

Rootkeys = {
	Endpoints.SEARCH_USER.value: "User",
	Endpoints.TOP_ALLIANCES.value: "Alliance",
	Endpoints.GET_ALLIANCE.value: "Alliance",
	Endpoints.ALLIANCE_USERS.value: "User",
	Endpoints.GET_VERSION.value: "Setting",
	Endpoints.GET_DIVISIONS.value: 'DivisionDesign',
	Endpoints.SHIP_DESIGNS.value: 'ShipDesign',
	Endpoints.INSPECT_SHIP.value: "InspectShip",
	Endpoints.SEND_MESSAGE.value: "Message"
}

CURRENT_SETTINGS = ET.fromstring(requests.get('https://api2.pixelstarships.com/' + Endpoints.GET_VERSION.value, params={'languageKey': 'ru', 'deviceType': 'DeviceTypeAndroid'}).text).find(f'.//{Rootkeys[Endpoints.GET_VERSION.value]}')

PRODUCTION = CURRENT_SETTINGS.attrib.get('ProductionServer') or 'api2.pixelstarships.com'
PRODUCTION = "https://" + PRODUCTION

Divisions = {
	0: None,
	1: "A",
	2: "B",
	3: "C",
	4: "D",
}

TOKEN_RE = "[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}"
DEVICE_RE = "[a-f0-9]{12}"