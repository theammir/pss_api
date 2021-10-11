from .constants import Divisions, PRODUCTION
import requests

import logging
logger = logging.getLogger("pss_api")

class Model:
	def __init__(self, data):
		self.xml = data
		self.attrib = data.attrib

class Sprite(Model):
	def __init__(self, container):
		self.img_bytes = None
		self.img_url = None
		self.id = None
		if isinstance(container, str):
			container = int(container)
		if isinstance(container, int):
			r = requests.get(f'{PRODUCTION}/FileService/DownloadSprite', params={'spriteid': container})
			logger.info(f'[GET {r.status_code}] FileService/DownloadSprite {dict(spriteid=container)}')
			r.raise_for_status()
			self.id = container
			self.img_bytes = r.content
			self.img_url = r.url
		else:
			self.container = container
			self.img_bytes = container.http_resp.content
			self.id = container.r_params['spriteid']
			self.img_url = container.http_resp.url

	def to_file(self, filename: str, mode: str = 'wb'):
		with open(filename, mode) as f:
			f.write(self.img_bytes)

class DivisionDesign(Model):
	def __init__(self, xml):
		super().__init__(xml)

		self.id = int(self.attrib['DivisionDesignId'])

		self.min_rank = int(self.attrib["MinRank"])
		self.max_rank = int(self.attrib['MaxRank'])
		self.min_index = self.min_rank - 1
		self.max_index = self.max_rank - 1

		self.logo_sprite = Sprite(self.attrib['LogoSpriteId'])
		self.background_sprite = Sprite(self.attrib['BackgroundSpriteId'])
		self.banner_sprite = [Sprite(i) for i in self.attrib["BannerSpriteIds"].split(',')]

class Alliance(Model):
	def __init__(self, data):
		super().__init__(data)
		
		self.id = int(self.attrib['AllianceId'])
		self.name = self.attrib['AllianceName']
		self.trophies = int(self.attrib["Trophy"])
		self.credits = int(self.attrib['Credits'])
		self.score = int(self.attrib["Score"])
		self.sprite = Sprite(self.attrib["AllianceSpriteId"])
		self.station_id = int(self.attrib["AllianceShipUserId"])
		self.members = int(self.attrib['NumberOfMembers'])
		self.approved_members = int(self.attrib["NumberOfApprovedMembers"])
		self.trophies_reqiured = int(self.attrib["MinTrophyRequired"])

		self.division = Divisions[int(self.attrib['DivisionDesignId'])]

		self.approval_required = bool(self.attrib["RequiresApproval"])
		self.requires_approval = self.approval_required
		self.needs_approval = self.approval_required

		self.description = self.attrib["AllianceDescription"]

class Player(Model):
	def __init__(self, xml):
		super().__init__(xml)

		self.name = self.attrib['Name']
		self.nick = self.name
		self.id = int(self.attrib["Id"])
		self.sprite = Sprite(self.attrib['IconSpriteId'])
		self.user_type = self.attrib['UserType']
		self.last_login_at = self.attrib['LastLoginDate']
		self.last_active_at = self.attrib["LastHeartBeatDate"]

		self.season = None
		if (season := self.xml.find('UserSeason')):
			self.season = Season(season, self)

		self.trophies = int(self.attrib["Trophy"])
		self.highest_trophies = int(self.attrib["HighestTrophy"])
		self.stars = int(self.attrib["AllianceScore"])
		self.tour_battles_left = int(self.attrib["TournamentBonusScore"])
		self.tour_battles_done = 6 - self.tour_battles_left

		self.alliance = None
		if (alliance := self.xml.find("Alliance")):
			self.alliance = Alliance(alliance)

		self.alliance_membership = self.attrib["AllianceMembership"]
		self.alliance_joined_at = self.attrib["AllianceJoinDate"]

		self.alliance_donation = int(self.attrib["AllianceSupplyDonation"])
		self.total_donation = int(self.attrib["TotalSupplyDonation"])
		self.crew_donated = int(self.attrib["CrewDonated"])
		self.crew_received = int(self.attrib["CrewReceived"])

		self.atk_wins = int(self.attrib["PVPAttackWins"])
		self.atk_losses = int(self.attrib['PVPAttackLosses'])
		self.atk_draws = int(self.attrib["PVPAttackDraws"])
		self.def_wins = int(self.attrib["PVPDefenceWins"])
		self.def_losses = int(self.attrib["PVPDefenceLosses"])
		self.def_draws = int(self.attrib["PVPDefenceDraws"])

class Season(Model):
	def __init__(self, xml, player=None):
		super().__init__(xml)

		self.id = int(self.attrib['UserSeasonId'])
		self.design_id = int(self.attrib['SeasonDesignId'])
		self.user_id = int(self.attrib['UserId'])
		self.user = player
		self.points = int(self.attrib['Points'])
		self.vip_status = self.attrib['PurchaseVIPStatus']

class ShipDesign(Model):
	# https://codebeautify.org/xmlviewer/cb3064d0
	def __init__(self, xml):
		super().__init__(xml)

		self.id = int(self.attrib["ShipDesignId"])
		self.name = int(self.attrib['ShipDesignName'])
		self.description = self.attrib["ShipDescription"]
		self.level = int(self.attrib['ShipLevel'])
		self.hp = int(self.attrib["Hp"])
		self.health = self.hp
		self.type = self.attrib["ShipType"]

		self.rows = int(self.attrib["Rows"])
		self.columns = int(self.attrib["Columns"])
		self.xlength, self.ylength = self.rows, self.columns

		self.repair_time = int(self.attrib["RepairTime"])
		self.upgrade_time = int(self.attrib["UpgradeTime"])

		self.mineral_cost = int(self.attrib["MineralCost"])
		self.starbucks_cost = int(self.attrib["StarbucksCost"])

		self.exterior_sprite = Sprite(self.attrib["ExteriorSpriteId"])
		self.interior_sprite = Sprite(self.attrib["InteriorSpriteId"])
		self.lift_sprite = Sprite(self.attrib[""])
		self.logo_sprite = Sprite(self.attrib["LogoSpriteId"])
		self.mini_sprite = Sprite(self.attrib["MiniShipSpriteId"])

		self.race_id = int(self.attrib["RaceId"])
	
class Ship(Model):
	# https://codebeautify.org/xmlviewer/cb579425
	def __init__(self, xml):
		super().__init__(xml)

		self.id = int(self.attrib["ShipId"])
		self.design_id = int(self.attrib["ShipDesignId"])

		self.hp = int(self.attrib["Hp"])
		self.health = self.hp
		self.status = self.attrib["ShipStatus"]
		self.shield = int(self.attrib["Shield"])

		self.hsv = (float(self.attrib["HueValue"]), float(self.attrib["SaturationValue"]), float(self.attrib["BrightnessValue"]))
		self.stickers = self.process_stickers(self.attrib["StickerString"])

		self.current_star_system_id = self.attrib["StarSystemId"]
		self.previous_star_system_id = self.attrib["FromStarSystemId"]
		self.next_star_system_id = self.attrib["NextStarSystemId"]

	def process_stickers(self, string):
		result_map = {}
		stickers = string.split("|")
		for sticker in stickers:
			sticker = sticker.split("@")
			sticker_id = int(sticker[0])
			sticker_params = tuple([float(i) for i in sticker[1].split('-')])

			result_map[sticker_id] = sticker_params

		return result_map
	
class InspectShipData(Model):
	def __init__(self, xml):
		super().__init__(xml)

		self.user = Player(self.xml.find("User"))
		self.ship = Ship(self.xml.find("Ship"))
		
class Message(Model):
	def __init__(self, xml):
		super().__init__(xml)

		self.id = self.attrib["MessageId"]
		self.user_id = self.attrib["UserId"]
		self.user_name = self.attrib["UserName"]

		self.fleet_name = self.attrib["AllianceName"]
		self.alliance_name = self.fleet_name

		self.text = self.attrib["Message"]
		self.content = self.text
		self.message = self.text

		self.date = self.attrib["MessageDate"]
		self.trophies = self.attrib["Trophy"]


def return_model(target_type, container):
	logger.info(f"[MDL] Initializing {target_type.__module__}.{target_type.__name__} model")
	if (target_type is Sprite):
		return Sprite(container)

	mdl = None
	if isinstance(container.xml, list):
		temp = []
		for element in container.xml:
			temp.append(target_type(element))
		mdl = temp
	else:
		mdl = target_type(container.xml)

	return mdl