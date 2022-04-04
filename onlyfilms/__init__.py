import logging
import logging.config

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DB = 'sqlite:///films.db'

logging.config.fileConfig(
    './onlyfilms/logger.conf', disable_existing_loggers=False
)
logger = logging.getLogger(__name__)

engine = create_engine(DB)
Base = declarative_base()
Session = sessionmaker(engine)
