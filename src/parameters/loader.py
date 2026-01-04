import json
from src.utils.logger import logger
from src.parameters.config_model import AppConfig 

def load_parameters(path: str) -> AppConfig:

    try:
        with open(path, "r", encoding='utf-8') as file:
            logger.info(f"Reading parameter file: {path}")
            config_data = json.load(file)
            
            #Pydantic - make Object AppConfig, and auto Validation 
            return AppConfig(**config_data)
            
    except FileNotFoundError:
        logger.error(f"Error: The file '{path}' was not found.")
        raise 
        
    except Exception as e:
        logger.error(f"Failed to load parameters: {e}")
        raise