import logging
from datetime import datetime
import os


DEFAULT_LOGGER_DIR:str = 'logs'
DEFAULT_LOGGER_LEVEL:int = logging.INFO


class ServiceLogger:
    logger = None
        
    @staticmethod
    def init_logger(logger_name:str = None,
                    log_dir:str = DEFAULT_LOGGER_DIR,
                    logging_level:int = DEFAULT_LOGGER_LEVEL,
                    days:int=7)->None:
        
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        ct: datetime = datetime.now()
        name = logger_name or (ct.strftime('%Y-%m-%d') + ".log")
        if ServiceLogger.logger is None:
            ServiceLogger.logger = logging.getLogger(name=os.path.join(log_dir, name)) 
            ServiceLogger.logger.setLevel(logging_level)  
            handler = logging.FileHandler(os.path.join(log_dir, name))
            handler.setLevel(logging.DEBUG)       
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            ServiceLogger.logger.addHandler(handler)               
        
            ServiceLogger.clean_up_log_dir(log_dir, days)
        
    @staticmethod
    def is_initialized()->bool:
        return ServiceLogger.logger is not None
    
    @staticmethod    
    def log_error(name:str, msg:str)->None:
        ServiceLogger.logger.error(f'{name}: {msg}')
    
    @staticmethod    
    def log_info(name:str, msg:str)->None:
        ServiceLogger.logger.info(f'{name}: {msg}') 
        
    @staticmethod
    def log_warning(name:str, msg:str)->None:
        ServiceLogger.logger.warning(f'{name}: {msg}') 
        
    @staticmethod
    def log_debug(name:str, msg:str)->None:    
        ServiceLogger.logger.debug(f'{name}: {msg}')
        
    @staticmethod
    def log_critical(name:str, msg:str)->None:    
        ServiceLogger.logger.critical(f'{name}: {msg}')
        
    @staticmethod
    def log_exception(name:str, msg:str)->None:    
        ServiceLogger.logger.exception(f'{name}: {msg}')
     
    @staticmethod    
    def clean_up_log_dir(dir:str, days)->None:
        now = datetime.now()
        for file in os.listdir(dir):
            if file.endswith('.log'):
                file_path = os.path.join(dir, file)
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                if (now - file_time).days > days:
                    os.remove(file_path)
