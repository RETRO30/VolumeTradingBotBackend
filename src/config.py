from dataclasses import dataclass
import os
from dotenv import load_dotenv

@dataclass(frozen=True, slots=True)
class ConfigData:
    database_url: str
    jwt_secret: str
    port: int
    
    
def load_config() -> ConfigData:
    if not os.getenv("DATABASE_URL"):
        env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        load_dotenv(dotenv_path=env_path)
    
    return ConfigData(
        database_url=os.getenv("DATABASE_URL"),
        jwt_secret=os.getenv("JWT_SECRET"),
        port=int(os.getenv("PORT", 8000))
    )
    
Config = load_config()
