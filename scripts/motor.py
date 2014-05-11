'''
The MIT License (MIT)

Copyright (c) 2014 Hu Dou 

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

import RPi.GPIO as gpio
import time 
import sys
import zmq
import signal

# Define control pins using BOARD numbering
left_front_wheel_forward_pin = 7
left_front_wheel_backward_pin = 11
right_front_wheel_forward_pin = 12
right_front_wheel_backward_pin = 13
left_rear_wheel_forward_pin = 15
left_rear_wheel_backward_pin = 16
right_rear_wheel_forward_pin = 18
right_rear_wheel_backward_pin = 22

# put all pins in a list for convenience
control_pins = [left_front_wheel_forward_pin, left_front_wheel_backward_pin, \
                right_front_wheel_forward_pin, right_front_wheel_backward_pin, \
                left_rear_wheel_forward_pin, left_rear_wheel_backward_pin,
                right_rear_wheel_forward_pin, right_rear_wheel_backward_pin]


def setup():
	'''
	Setup the GPIO pins
	'''
	gpio.setmode(gpio.BOARD)
	gpio.setwarnings(False)	# Suppress the warnings complaining that the channel has been configured ...
	[gpio.setup(p, gpio.OUT) for p in control_pins]
	

def left_front_wheel_forward():
	gpio.output(left_front_wheel_forward_pin, True)
	gpio.output(left_front_wheel_backward_pin, False)

def left_front_wheel_backward():
        gpio.output(left_front_wheel_forward_pin, False)
        gpio.output(left_front_wheel_backward_pin, True)

def right_front_wheel_forward():
	gpio.output(right_front_wheel_forward_pin, True)
	gpio.output(right_front_wheel_backward_pin, False)

def right_front_wheel_backward():
	gpio.output(right_front_wheel_forward_pin, False)
	gpio.output(right_front_wheel_backward_pin, True)

def left_rear_wheel_forward():
	gpio.output(left_rear_wheel_forward_pin, True)
	gpio.output(left_rear_wheel_backward_pin, False)

def left_rear_wheel_backward():
	gpio.output(left_rear_wheel_forward_pin, False)
	gpio.output(left_rear_wheel_backward_pin, True)

def right_rear_wheel_forward():
	gpio.output(right_rear_wheel_forward_pin, True)
	gpio.output(right_rear_wheel_backward_pin, False)

def right_rear_wheel_backward():
	gpio.output(right_rear_wheel_forward_pin, False)
	gpio.output(right_rear_wheel_backward_pin, True)
	 
def car_forward():
	left_front_wheel_forward()
	right_front_wheel_forward()
	left_rear_wheel_forward()
	right_rear_wheel_forward()

def car_backward():
	left_front_wheel_backward()
	right_front_wheel_backward()
	left_rear_wheel_backward()
	right_rear_wheel_backward()

def car_stop():
	[gpio.output(p, False) for p in control_pins]

def car_left_forward():
	'''
	Make the car turn left forward by turning the right
	wheels forward and left wheels backward
	'''
	left_front_wheel_backward()
	left_rear_wheel_backward()
	right_front_wheel_forward()
	right_rear_wheel_forward()

def car_right_forward():
	'''
	Make the car turn right forward by turning the left 
	wheels forward and right wheels backward
	'''
	left_front_wheel_forward()
	left_rear_wheel_forward()
	right_front_wheel_backward()
	right_rear_wheel_backward()

def test():
	'''
	A quick test of all motions
	'''
	car_forward()
	time.sleep(2)
	car_backward()
	time.sleep(2)
	car_left_forward()
	time.sleep(2)
	car_right_forward()
	time.sleep(2)
	car_stop()

#######################################################
# Car control commands:
#  f: forward
#  b: backward
#  lf: left forward
#  rf: right forward
#  t: stop the car
#######################################################
commands = {
	'f' : car_forward,
	'b' : car_backward,
	'lf': car_left_forward,
	'rf': car_right_forward,
	't' : car_stop
}


#######################################################
# To connect to the server, run a program that implements
# a zeromq client, and send commands to the server as
# specified above.
#######################################################
def run_control_server():
	'''
	Run a zeromq server to receive commands from the clients
	Use TCP port: 5555
	Valid commands are:
	 car control commands
	 q: quit the server
	'''
	context = zmq.Context()
	socket = context.socket(zmq.PAIR) # Use PAIR sockets
	print 'Listening to port 5555'
	socket.bind('tcp://*:5555')

	def sigint_handler(sig, frame):
		'''
		Intercept the SIGINT signal, close the socket, and exit
		gracefully.
		'''
		print '\nReceived Ctrl-C'
		print 'Closing the socket ...',
		socket.close()
		print 'done'
		sys.exit(0)
	
	# Set our own sigint handler
	signal.signal(signal.SIGINT, sigint_handler)

	while True:
		cmd = socket.recv()
		print 'Control server: received command ', cmd
		if cmd in commands:
			commands[cmd]()
			socket.send('OK ' + cmd)
		elif cmd == 'q':
			car_stop()	# stop the car before close
			socket.send('OK. Quit')
			socket.close()
			context.term()
			break
		else:
			socket.send('Err: Unknown command ' + cmd)
			print 'Invalid command: ', cmd

if __name__ == '__main__':
	setup()
	#test()	
	run_control_server()

