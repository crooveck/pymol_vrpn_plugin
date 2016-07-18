# VRPN
import sys
sys.path.append("/home/crooveck/workspace/vrpn/build_new/python_vrpn")
import vrpn_Tracker
import vrpn_Button
import vrpn_ForceDevice
# transformations
sys.path.append(".")
from transformations import *
# inne
from time import *

print "\t+--------------------------------+"
print "\t|   SensAble Phantom Omni Test   |"
print "\t+--------------------------------+"

def quat_to_ogl_matrix(qx,qy,qz,qw):
    print("qx=%f, qy=%f, qz=%f, qw=%f" % (qx,qy,qz,qw))
    return (1,2,3,4,11,22,33,44,111,222,333,444,1111,2222,3333,4444)
    

def button_handler(userdata, t):
    button = t[0]
    state = t[1]
    
    msg = ""
    if(state==1):
        msg += "Wcisnieto "
    else:
        msg += "Puszczono "
        
    msg += "przycisk "
    
    if(button==1):
        msg += "gorny."
    else:
        msg += "dolny."
    
    print msg

def tracker_handler(userdata, t):
    global previous_orientation
    
    position=(t[1],t[2],t[3])
    current_orientation=(t[5],t[6],t[7],t[4])
    
    print("\n-------------------")
    print("POZYCJA: (%f,%f,%f)" % (position[0],position[1],position[2]))

    if(previous_orientation==0): 
        previous_orientation=current_orientation

    print("ORIENTACJA:")
    print("    poprzednia: (%f,%f,%f,%f)" % (previous_orientation[0],previous_orientation[1],previous_orientation[2],previous_orientation[3]))
    print("    obecna: (%f,%f,%f,%f)" % (current_orientation[0],current_orientation[1],current_orientation[2],current_orientation[3]))
    
    # current_orientation=(t[5],t[6],t[7],t[4])   # inny format kwaterniona do transformations.py niz dostaje z VRPN
    # przy pierwszym uruchomieniu 
    # gdy nie ma poprzedniej orientacji 
    if(previous_orientation==0):
        previous_orientation=current_orientation
    
    rotation_quaternion=quaternion_multiply(quaternion_inverse(current_orientation),previous_orientation)
 
    print("ROTACJA:")
    print("\tkwaternion: (%f,%f,%f,%f)" % (rotation_quaternion[0],rotation_quaternion[1],
                                            rotation_quaternion[2],rotation_quaternion[3]))
                                   
    rotation_matrix = quaternion_matrix(rotation_quaternion)                             
    (rotation_angle,rotation_axis,point) = rotation_from_matrix(rotation_matrix)

    print("\tangle=%f\taxis: (x=%f,y=%f,z=%f)" % (rotation_angle,rotation_axis[0],rotation_axis[1],rotation_axis[2]))

#    # zapamietuje dane z obecnej orientacji
    previous_orientation=current_orientation
    
        
def force_handler(userdata, t):
    print "sila",t,userdata
    

PHANTOM_LOCATION = "phantom0@172.21.5.161"

tracker = vrpn_Tracker.vrpn_Tracker_Remote(PHANTOM_LOCATION)
vrpn_Tracker.register_tracker_change_handler(tracker_handler)
vrpn_Tracker.vrpn_Tracker_Remote.register_change_handler(tracker, None, vrpn_Tracker.get_tracker_change_handler())

button = vrpn_Button.vrpn_Button_Remote(PHANTOM_LOCATION)
vrpn_Button.register_button_change_handler(button_handler)
vrpn_Button.vrpn_Button_Remote.register_change_handler(button, None, vrpn_Button.get_button_change_handler())

forceDevice = vrpn_ForceDevice.vrpn_ForceDevice_Remote(PHANTOM_LOCATION)
vrpn_ForceDevice.register_force_change_handler(force_handler)
vrpn_ForceDevice.vrpn_ForceDevice_Remote.register_force_change_handler(forceDevice, None, vrpn_ForceDevice.get_force_change_handler())

#forceDevice.set_plane(0.0, 1.0, 0.0, 0.0)
#forceDevice.setSurfaceKspring(1.0)
#forceDevice.setSurfaceKdamping(0.1)
#forceDevice.setSurfaceFstatic(0.7)
#forceDevice.setSurfaceFdynamic(0.3)
#forceDevice.setRecoveryTime(3)
#forceDevice.startSurface()

#forceDevice.setFF_Origin(0.0, 0.0, 0.0)
#forceDevice.setFF_Radius(1.0)
#forceDevice.setFF_Force(0.5, 0.5, 0)
#forceDevice.sendForceField()

forceDevice.setConstraintMode(forceDevice.POINT_CONSTRAINT)
forceDevice.setConstraintKSpring(100.0)
forceDevice.setConstraintPoint(0.0, 0.0, 0.0)   # przeciazona metoda, napisana przeze mnie w vrpn_ForceDevice.h/C
forceDevice.enableConstraint(1);

previous_orientation=0

# czekam na polaczenie z serwerem

print forceDevice.connectionAvailable()

while True:
    tracker.mainloop()
    button.mainloop()
    forceDevice.mainloop()

forceDevice.stopSurface()
    
