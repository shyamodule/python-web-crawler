import logging 
  
#Create and configure logger 
logging.basicConfig(filename="log-file.log", format='%(asctime)s %(levelname)s: %(message)s',) 
  
#Creating an object 
logger=logging.getLogger() 
  
#Setting the threshold of logger to DEBUG 
logger.setLevel(logging.DEBUG) 

