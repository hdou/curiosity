import RPi.GPIO as gpio
import time 
import sys

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

def show_usage():
	print "usage: sudo motor.py <f | b | lf | rf | t>"
	print "    f: forward"
	print "    b: backward"
	print "    lf: left forward"
	print "    rf: right forward"
	print "    t: stop"

def car_control():
	if len(sys.argv) == 2:
		cmd = sys.argv[1]
		if cmd == 'f':
			car_forward()
		elif cmd == 'b':
			car_backward()
		elif cmd == 'lf':
			car_left_forward()
		elif cmd == 'rf':
			car_right_forward()
		elif cmd == 't':
			car_stop()
		else:
			show_usage()
			raise Exception("Invalid command")
	else:
		show_usage()
		raise Exception("Invalid arguments")

if __name__ == '__main__':
	setup()
	#test()	
	car_control()


