import pss_module

import logging
logging.basicConfig(format="%(asctime)s [%(name)s %(levelname)s] %(message)s", datefmt="%H:%M:%S", level=logging.INFO)
logger = logging.getLogger("pss_api")

session = pss_module.login.from_device_key('e84bbed1c154268c')

session.send_message("Печеньки они и с помадкой печеньки", "public-ru")