import json

import roslibpy


class RosClientDisconnected(Exception):
    pass


class RosbridgeJSONConnector:
    def __init__(self, host='127.0.0.1', port=9090, topic='object_detection'):

        self.client = roslibpy.Ros(host=host, port=port)
        
        self.client.on_ready(lambda: print(f'ROS connected for {topic}: ', self.client.is_connected))

        self.client.run()
        self.talker = roslibpy.Topic(self.client, topic, 'std_msgs/String')
        self.topic = topic
        
    def __del__(self):
        self.talker.unadvertise()
        self.client.terminate()

    def is_connected(self):
        return self.client.is_connected

    def publish_message(self, message_dict):
        if not self.is_connected():
            raise RosClientDisconnected(f'Topic {self.topic} is not connected')

        self.talker.publish(roslibpy.Message({'data': json.dumps(message_dict)}))

