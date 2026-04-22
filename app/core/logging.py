import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger configurado.
    Todos los logs van a stdout con trace_id cuando sea posible.
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger