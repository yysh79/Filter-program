import logging

logging.basicConfig(
    filename='my_log.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode= 'w',  
     )
