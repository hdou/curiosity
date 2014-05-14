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
import threading

# Motor control pins using BOARD numbering
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


# IR range sensor (rs) pins
rs_trigger = 3
rs_input = 5

# Symbols used for the status of the car
Stopped = 1
Forward = 2
Backward = 3
LeftForward = 5
RightForward = 6

# Global variable to store the current car status
car_status = Stopped

# Lock to pretect race condition during car control and update car status
car_control_lock = threading.RLock()

def setup():
	'''
	Setup the GPIO pins
	'''
	gpio.setmode(gpio.BOARD)
	gpio.setwarnings(False)	# Suppress the warnings complaining that the channel has been configured ...
	# motor control pins
	[gpio.setup(p, gpio.OUT) for p in control_pins]
	
	# range sensor pins
	gpio.setup(rs_trigger, gpio.OUT)
	gpio.setup(rs_input, gpio.IN)
	# set the trigger to low as the initial condition
	gpio.output(rs_trigger, gpio.LOW)	


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
	with car_control_lock:
		left_front_wheel_forward()
		right_front_wheel_forward()
		left_rear_wheel_forward()
		right_rear_wheel_forward()
		global car_status
		car_status = Forward

def car_backward():
	with car_control_lock:
		left_front_wheel_backward()
		right_front_wheel_backward()
		left_rear_wheel_backward()
		right_rear_wheel_backward()
		global car_status
		car_status = Backward

def car_stop():
	with car_control_lock:
		[gpio.output(p, False) for p in control_pins]
		global car_status
		car_status = Stopped

def car_left_forward():
	'''
	Make the car turn left forward by turning the right
	wheels forward and left wheels backward
	'''
	with car_control_lock:
		left_front_wheel_backward()
		left_rear_wheel_backward()
		right_front_wheel_forward()
		right_rear_wheel_forward()
		global car_status
		car_status = LeftForward

def car_right_forward():
	'''
	Make the car turn right forward by turning the left 
	wheels forward and right wheels backward
	'''
	with car_control_lock:
		left_front_wheel_forward()
		left_rear_wheel_forward()
		right_front_wheel_backward()
		right_rear_wheel_backward()
		global car_status
		car_status = RightForward

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

	# flag to indicate we are stopping the server
	# use a single element array so it can be used in closure
	# of dist_func. Simple variable won't work
	stop_server = [False]

	# Start another thread to detect distance
	# The main function of the thread
	def dist_func():
		print 'Distance detection thread started'
		while not stop_server[0]:
			# send a 10us pulse to the range sensor trigger
			gpio.output(rs_trigger, True)
			time.sleep(0.00001)
			gpio.output(rs_trigger, False)
			# Waiting for the echo to return
			# Sleep 100us in between so I don't hog the CPU
			# this gives me a 1.7cm resolution
			# The max distance the sensor can detect is about
			# 5 meters, which takes ~30ms for the echo to 
			# get back. If we still don't get the echo after
			# 30ms, the distance is considered infinite, and
			# I restart the loop again.
			wait_for_echo_count = 0 
			while gpio.input(rs_input) == 0:
				time.sleep(0.0001)
				wait_for_echo_count += 1
				if wait_for_echo_count == 300:
					break
			if wait_for_echo_count == 300:
				print 'Distance: inf'
			else:	 	
				starttime = time.time()
				while gpio.input(rs_input) == 1:
					time.sleep(0.0001)
				stoptime = time.time()
				dist = 170 * (stoptime - starttime)
				print 'Distance: %.2fm' % dist
				# If distance is less than 15cm, stop the car
				global car_status
				if dist <= 0.15:
					with car_control_lock:
						if car_status == Forward:
							car_stop()
			# sleep for a while
			time.sleep(0.05)
		print 'Distance detection thread stopped'

	# Start the thread
	dist_detection_thread = threading.Thread(target=dist_func)
	dist_detection_thread.start() 
		
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
		print 'Stopping distance detection thread...',
		stop_server[0] = True
		dist_detection_thread.join()
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
			stop_server[0] = True
			dist_detection_thread.join()
			break
		else:
			socket.send('Err: Unknown command ' + cmd)
			print 'Invalid command: ', cmd

if __name__ == '__main__':
	setup()
	if len(sys.argv) == 2 and sys.argv[1] == 'test':
		test()
	else:
		run_control_server()

