from logging import (
    Logger, 
    INFO, 
    getLogger,
    FileHandler,
    Formatter
    )
    
from datetime import datetime
import os


DEFAULT_LOGGER_DIR:str = 'logs'
DEFAULT_LOGGER_LEVEL:int = INFO
LOG_NAME:str = 'Homeboit_Logger'


class ServiceLogger:
    logger: Logger | None = None
    
    @staticmethod
    def init_logger(logger_name:str| None = None,
                    log_dir:str = DEFAULT_LOGGER_DIR,
                    logging_level:int = DEFAULT_LOGGER_LEVEL,
                    days:int=7)->None:
        
        ct: datetime = datetime.now()
        name = logger_name or (ct.strftime('%Y-%m-%d') + ".log")
        if ServiceLogger.logger is None:
            ServiceLogger.logger = getLogger(name=os.path.join(log_dir, name)) 
            ServiceLogger.logger.setLevel(logging_level)  
            handler = FileHandler(os.path.join(log_dir, name))
            handler.setLevel(logging_level)       
            formatter = Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            ServiceLogger.logger.addHandler(handler)               
        
            ServiceLogger.clean_up_log_dir(log_dir, days)
        
    @staticmethod
    def is_initialized()->bool:
        return ServiceLogger.logger is not None
    
    @staticmethod    
    def log_error(name:str, msg:str)->None:
        if ServiceLogger.logger is not None:
            ServiceLogger.logger.error(f'{name}: {msg}')
    
    @staticmethod    
    def log_info(name:str, msg:str)->None:
        if ServiceLogger.logger is not None:
            ServiceLogger.logger.info(f'{name}: {msg}') 
        
    @staticmethod
    def log_warning(name:str, msg:str)->None:
        if ServiceLogger.logger is not None:
            ServiceLogger.logger.warning(f'{name}: {msg}') 
        
    @staticmethod
    def log_debug(name:str, msg:str)->None: 
        if ServiceLogger.logger is not None:   
            ServiceLogger.logger.debug(f'{name}: {msg}')
        
    @staticmethod
    def log_critical(name:str, msg:str)->None:    
        if ServiceLogger.logger is not None:   
            ServiceLogger.logger.critical(f'{name}: {msg}')
        
    @staticmethod
    def log_exception(name:str, msg:str)->None:    
        if ServiceLogger.logger is not None:   
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
