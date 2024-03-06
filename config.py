
import logging
import os
from pathlib import (
    Path,
)

from dotenv import (
    load_dotenv,
)


load_dotenv()
logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger(__name__)

pictures_dir = Path("static")

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE = os.getenv("POSTGRES_DB")
USER = os.getenv("POSTGRES_USER")
HOST = os.getenv("POSTGRES_HOST")
PORT = os.getenv("POSTGRES_PORT")
PASSWORD = os.getenv("POSTGRES_PASSWORD")
GROUP_ID = os.getenv("GROUP_ID")
