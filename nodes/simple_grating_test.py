#!/usr/bin/env python
import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation
from VisionEgg.Gratings import *


def callback(self, data):
    print 'callback'

    

if __name__ == '__main__':
    # Initialize OpenGL graphics screen.
    #screen = get_default_screen()
    screen = VisionEgg.Core.Screen( size = (1280,720) )
    screen.parameters.bgcolor = (0,0,0,0)

    checkerboard_wall = SinGrating2D(   position         = (1100,700),
                                        anchor           = 'center',
                                        size             = ( 1500 , 1500 ),
                                        spatial_freq     = 8.0 / screen.size[0], # units of cycles/pixel
                                        temporal_freq_hz = 1,
                                        orientation      = 0. )


                     
    #########################
    #  Create the viewport  #
    #########################

    # Create a viewport for the target
    viewport_left = Viewport( screen=screen, position=(0,0), size=(1920,160), stimuli=[checkerboard_wall] )

    p = Presentation(go_duration=('20', 'seconds'),viewports=[viewport_left,]) 
    
    p.go()
