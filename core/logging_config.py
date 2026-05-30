import logging, os
LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs'); os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.FileHandler(os.path.join(LOG_DIR, 'smartfurniture.log')), logging.StreamHandler()])
logger = logging.getLogger('SmartFurniture')
