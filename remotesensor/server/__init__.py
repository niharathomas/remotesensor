import tornado.ioloop
import tornado.web
from remotesensor.database.sensorreadings import SensorReadingWriter
import json 
import logging
import traceback
logging.basicConfig(filename='/var/log/sensors/server.log',level=logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(ch)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.send_error(404)
    def post(self):
        self.send_error(404)

class SensorHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        tornado.web.RequestHandler.__init__(self, application, request, **kwargs)
        logger.debug('Initalizing Sensor Handler and connecting to mongo at localhost ')
        self._srw = SensorReadingWriter()
        #self._srw = SensorReadingWriter(hostname='54.85.111.126')
    def get(self):
        sensorid = self.get_argument("sensorid", None)
        if sensorid :
            self.write(tornado.escape.json_encode(self._srw.findBySensor(int(sensorid))))
        else:
            self.set_status(500)
            self.write('INVALID REQUEST')
            
    def post(self):
        data_json = None
        indata = None
        try:
            indata = tornado.escape.utf8(self.request.body)
            data_json = json.loads(indata)
        except:
            logger.error(traceback.format_exc()+'\ninput data is ' + indata)
            self.set_status(500)
            self.write('FAILED TO PARSE INPUT DATA')
            
        try:
            sensorid = data_json['id']
            t = data_json['t']
            if t < -25.00 or t > 110.00 :
                self.set_status(500)
                logger.error('Wrong temperature value => {} from sensor {} ' .format(t, sensorid))
                return self.write('Wrong temperature value =>' +  str(t))
        except:
            logger.error(traceback.format_exc() + '\ninput data is ' + indata)
            self.set_status(500)
            self.write('FAILED TO SAVE')
            return
        logger.debug( "saved Temperature" + str(data_json) )
        self.write('SUCCESS')
        
application = tornado.web.Application([ (r"/", MainHandler), (r"/sensor", SensorHandler) ])

if __name__ == "__main__":
    port = 12000
    application.listen(port)
    print 'starting at port:', 12000
    tornado.ioloop.IOLoop.current().start()