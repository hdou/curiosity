curiosity
=========

Use raspberry pi and web interface to control a toy car.

A plexiglass, about the size of a legal paper, is used as the chassis. 
A RPi, two L298N motor drive controller boards, and two battery packs 
are assembled on the board. One L298N controls two front wheels, and 
the other rear wheel. RPi's GPIO pins controls the wheels through the 
motor controllers as follows:

wheels                       RPi's GPIO (pin number)  
---------------------------------------------------------------------
left front wheel             GPIO 4 (7), and GPIO 17 (11)
right front wheel            GPIO 18 (12), and GPIO 27 (13)
left rear wheel              GPIO 22 (15), and GPIO 23 (16)
right rear wheel             GPIO 24 (18), and GPIO 25 (22)

Each wheel is controlled by two GPIO pins as follows:

Movement       GPIO #1          GPIO #2
---------------------------------------------------------------------
stop           False            False
forward        True             False
backward       False            True
               
