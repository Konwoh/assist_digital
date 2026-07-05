import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(filename=LOG_DIR / "error.log",
                    level=logging.ERROR,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    filemode='a')

logger = logging.getLogger(__name__)
