curiosity
=========

Use raspberry pi and web interface to control a toy car.

A plexiglass, about the size of a legal paper, is used as the chassis. 
A RPi, two L298N motor drive controller boards, and two battery packs 
are assembled on the board. One L298N controls two front wheels, and 
the other rear wheel. RPi's GPIO pins controls the wheels through the 
motor controllers as follows:

<table>
<tr><th>wheels</th><th>RPi's GPIO (pin number)</th></tr>
<tr><td>left front wheel</td><td>GPIO 4 (7), and GPIO 17 (11)</td></tr>
<tr><td>right front wheel</td><td>GPIO 18 (12), and GPIO 27 (13)</td></tr>
<tr><td>left rear wheel</td><td>GPIO 22 (15), and GPIO 23 (16)</td></tr>
<tr><td>right rear wheel</td><td>GPIO 24 (18), and GPIO 25 (22)</td></tr>
</table>

Each wheel is controlled by two GPIO pins as follows:

<table>
<tr><th>Movement</th><th>GPIO #1</th><th>GPIO #2</th></tr>
<tr><td>stop</td><td>False</td><td>False</td></tr>
<tr><td>forward</td><td>True</td><td>False</td></tr>
<tr><td>backward</td><td>False</td><td>True</td></tr>
</table>

