#!/usr/bin/env python
import sys, os
from optparse import OptionParser

import rospy
from flydra_triggers.msg import *
import time
from std_msgs.msg import *
import numpy as np

import csv

def trigger_function(x, y, z, vx, vy, vz):
    if x < 1 and y > 0.5:
        return True
    else:
        return False    
    
def get_temporal_frequency():
    values = [0, 4, 8, 16]
    index = np.random.randint(0,len(values))
    return values[index]

class Listener:
    def __init__(self, savedirectory='', trigger_function=trigger_function):
        self.trigger_function = trigger_function
        self.preferred_obj_id = None
        self.trigger_time = 0
        self.trigger_framenumber = 0
        self.refractory_time = 20
        self.temporal_frequency = 0
        
        filename = time.strftime("%Y%m%d_%H%M_triggerdata", time.localtime()) + '.csv'
        filename = os.path.join(savedirectory, filename)
        self.csvfile = open(filename, 'wb')
        self.datawrite = csv.writer(self.csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        
        info = ['preferred_object_id', 'trigger_framenumber', 'trigger_time', 'temporal_frequency']
        self.datawrite.writerow(info)
        
        # ROS
        rospy.init_node('listener', anonymous=True)
        self.pub = rospy.Publisher("preferred_obj_id", sine_grating)
        rospy.Subscriber("flydra_mainbrain_super_packets", flydra_mainbrain_super_packet, self.callback)
        
    def run(self):
        while (not rospy.is_shutdown()):
            rospy.spin()
        self.csvfile.close()
        
    def publish_preferred_object_id(self):
        info = [self.preferred_obj_id, self.trigger_framenumber, self.trigger_time, self.temporal_frequency]
        self.datawrite.writerow(info)
        self.pub.publish(self.preferred_obj_id, self.temporal_frequency)
        print 'TRIGGER: ', self.preferred_obj_id, self.trigger_framenumber, self.trigger_time, self.temporal_frequency
        
    def stop_preferred_object_id(self):
        self.pub.publish(0, 0)
        print 'TRIGGER OFF'
        print
        
    def callback(self, super_packet):
        for packet in super_packet.packets:
            time_acquired = packet.acquire_stamp.secs + packet.acquire_stamp.nsecs*10e-9
            
            if self.preferred_obj_id is not None:
                if time_acquired - self.trigger_time > self.refractory_time:
                    self.preferred_obj_id = None
                    self.trigger_time = 0
                    self.stop_preferred_object_id()
            
            if self.preferred_obj_id is None:
                for obj in packet.objects:
                    x,y,z = [obj.position.x, obj.position.y, obj.position.z]
                    vx,vy,vz = [obj.velocity.x, obj.velocity.y, obj.velocity.z]
                    trigger = self.trigger_function(x,y,z,vx,vy,vz)
                    
                    if trigger:
                        self.preferred_obj_id = obj.obj_id
                        self.trigger_time = time_acquired
                        self.trigger_framenumber = packet.framenumber
                        sign_of_temporal_frequency = np.sign(vx)
                        self.temporal_frequency = get_temporal_frequency()*sign_of_temporal_frequency
                        self.publish_preferred_object_id()
                        break

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("--path", type="str", dest="path", default='',
                        help="path to folder where to save data")
    (options, args) = parser.parse_args()
    
    path = options.path    
    
    listener = Listener(path)
    listener.run()
