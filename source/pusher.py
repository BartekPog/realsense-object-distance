
import json

from depth.depth_perceptor import DepthPerceptor
from rosbridge_connector import RosbridgeConnector


if __name__ == "__main__":
    dp = DepthPerceptor()
    connector = RosbridgeConnector(host='192.168.0.150')
    
    while connector.is_connected:
        connector.publish_message(json.dumps(dp.get_depth()))
