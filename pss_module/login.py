import hashlib
import random
import requests
import xml.etree.ElementTree as ET
from .constants import Endpoints, PRODUCTION
from . import atop
from datetime import datetime, timedelta

import logging
logger = logging.getLogger("pss_api")

class Device:
	def __init__(self, key=None, checksum=None):
		self.key = key
		if self.key:
			self.create_checksum()
		self.__token = None
		self.expires_at = None

	@property
	def token_expired(self):
		if not self.expires_at:
			return False
		return self.expires_at < datetime.now()

	@property
	def token(self):
		return self.get_access_token()

	def get_access_token(self):
		params={
				"deviceKey": self.key,
				"checksum": self.checksum,
				'isJailBroken': 'false',
				'deviceType': "DeviceTypeAndroid",
				'languageKey': 'ru',
				'advertisingKey': '""'
			}
		if not self.__token or self.token_expired:
			resp = requests.post(f"{PRODUCTION}/{Endpoints.USER_LOGIN.value}", params=params)
			root = ET.fromstring(resp.content.decode('utf-8'))
			logger.info(f'[POST {resp.status_code}] {Endpoints.USER_LOGIN.value} {params}')
			self.__token = root.find(".//UserLogin").attrib['accessToken']
			self.expires_at = datetime.now() + timedelta(hours=12)

			user_info = root.find(".//User").attrib
			logger.info(f"Logged as {user_info['Name']} ({user_info['Email']})")

		return self.__token


	def create_key(self):
		sequence = '0123456789abcdef'
		self.key = ''.join(
			random.choice(sequence)
			+ random.choice('26ae')
			+ random.choice(sequence)
			+ random.choice(sequence)
			+ random.choice(sequence)
			+ random.choice(sequence)
			+ random.choice(sequence)
			+ random.choice(sequence)
			+ random.choice(sequence)
			+ random.choice(sequence)
			+ random.choice(sequence)
			+ random.choice(sequence)
		)
		return self.key
	
	def create_checksum(self):
		self.checksum = hashlib.md5((self.key + 'DeviceTypeAndroid' + 'savysoda').encode('utf-8')).hexdigest()
		return self.checksum

	@staticmethod
	def create():
		new_device = Device()
		new_device.create_key()
		new_device.create_checksum()

		return new_device

class DeviceCollection:
	def __init__(self, devices=[], *, min_devices: int = 3):
		self.devices = devices
		self.next_index = None
		self.min_devices = min_devices

		if len(self.devices) < self.min_devices:
			for _ in range(self.min_devices - len(self.devices)):
				self.devices.append(Device.create())

		self.__token = None
		self.expires_at = None

	@property
	def next(self):
		if self.next_index is None:
			self.next_index = random.randrange(len(self.devices))

		if self.next_index >= len(self.devices):
			self.next_index = 0
		
		device = self.devices[self.next_index]
		self.next_index += 1

		return device

	@property
	def token_expired(self):
		if not self.expires_at:
			return False
		return self.expires_at < datetime.now()

	def get_access_token(self):
		success = False
		while not success:
			device = self.next
			try:
				token = device.get_access_token()
			except:
				pass
			finally:
				if token:
					success = True
		
		self.__token = token
		self.expires_at = device.expires_at
	
	
MAIN_COLLECTION = DeviceCollection(min_devices=5)

def create_device() -> Device:
	device_key = Device.create_key()
	device_checksum = Device.create_checksum(device_key)

	return Device(device_key, device_checksum)

def generate_token():
	return MAIN_COLLECTION.get_access_token()

def from_device_key(device_key):
	device = Device(device_key)

	return atop.Session(device.get_access_token())