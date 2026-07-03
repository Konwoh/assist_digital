import logging

logging.basicConfig(filename="logs/error.log",
                    level=logging.ERROR,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    filemode='a')

logger = logging.getLogger(__name__)
