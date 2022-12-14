import time
import json

import roslibpy


class RosbridgeConnector:
    def __init__(self, host='127.0.0.1', port=9090, topic='object_detection'):

        self.client = roslibpy.Ros(host=host, port=port)
        
        self.client.on_ready(lambda: print('Is ROS connected?', self.client.is_connected))

        self.client.run()
        self.talker = roslibpy.Topic(self.client, topic, 'std_msgs/String')

        
    def __del__(self):
        self.talker.unadvertise()
        self.client.terminate()

    def is_connected(self):
        return self.client.is_connected

    def publish_message(self, message):
        self.talker.publish(roslibpy.Message({'data': message}))

