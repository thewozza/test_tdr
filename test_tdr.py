import csv
import re
from netmiko import ConnectHandler
import os
import time
import subprocess

# these are just simple python formatted files with variables in them
from credentials import *

# this loads the devices we're working with from a simple CSV file
# I often alter this file depending on what I'm working on
switches = csv.DictReader(open("switches.csv"))

for row in switches:
	# first we test if the system is pingable - if it isn't we go to the next one
	# this is a very simple error handling mechanism - the script will crash if it can't reach a host
	response = os.system("ping -c 1 -w2 " + row['IP'] + " >/dev/null 2>&1")
	
	if response == 0:
		# this initializes the device object
		# it pulls the username/password/secret variables from a local file called 'credentials.py'
		# the IP is pulled from the 'switches.csv' file
		cisco_switch = {
		    'device_type': 'cisco_ios',
		    'ip': row['IP'],
		    'username': username,
		    'password': password,
		    'port' : 22,          # optional, defaults to 22
		    'secret': secret,     # optional, defaults to ''
		    'verbose': False,       # optional, defaults to False
		}
		
		# this actually logs into the device
		net_connect = ConnectHandler(**cisco_switch)
		net_connect.enable()
		# we gather a list of connected interfaces
		# there's no use testing ports with no patches
		# and most of our ports are not patched yet
		show_interface_status = net_connect.send_command('show interface status | i connected').split("\n")
		
		# here we issue the test commands
		for interface in show_interface_status:	
			# we clean up the output from show interface status
			# remove the extra tabs and replace with single spaces
			interface = " ".join(interface.split())
			intElement = interface.split(" ")
			
			# we skip anything that is a port channel or a 10GE interface
			if "Po" in intElement[0]:
				continue
			elif "Te" in intElement[0]:
				continue
			else:
				# assuming we've got an interface here we do the test
				test_tdr = 'test cable-diagnostics tdr interface ' + intElement[0]
				output = net_connect.send_command(test_tdr)
		
		# the test takes a while, one day I'll build in some logic to see when it is done
		# but for now we sleep
		time.sleep(10)
		
		# here we gather the results
		for interface in show_interface_status:	
			# we clean up the output from show interface status
			# remove the extra tabs and replace with single spaces
			interface = " ".join(interface.split())
			intElement = interface.split(" ")
			
			# we skip anything that is a port channel or a 10GE interface
			if "Po" in intElement[0]:
				continue
			elif "Te" in intElement[0]:
				continue
			else:
				# assuming we've got an interface here we look at the results
				show_tdr = 'show cable-diagnostics tdr interface ' + intElement[0]
				show_tdr_results = net_connect.send_command(show_tdr)
				
				# this is our final output that we start building here
				output = intElement[0]
				output = row['Switch'] + "," + intElement[0]
				
				# just initializing a temporary variable for results
				complete_results = ""
				
				# we go through the results line by line for an interface
				for tdr_output in show_tdr_results.split("\n"):
					
					# if we see a hyphen, we know that the results are the next line
					if "-" in tdr_output:
						# we clean up the output here
						# remove the extra tabs and replace with single spaces
						tdr_output = tdr_output.rstrip().lstrip()
						tdr_output =  " ".join(tdr_output.split())
						tdr_output = tdr_output.split(" ")
						
						# sometimes we get a blank line, this makes sure the
						# script doesn't crash
						try:
							tdr_output[1]
						except IndexError:
							continue
						
						# skip the line with hyphens
						if "---------" in tdr_output[0]:
							continue
						
						# here's the magic
						# the line with the interface in it (Gi1/0/2) is different
						# so we look for that and treat it differently
						if tdr_output[0] == intElement[0]:
							speed = tdr_output[1]
							if "Pair" in tdr_output[8]:
								status = tdr_output[10]
							else:
								status = tdr_output[9]
							length = tdr_output[4]
						else:
							if "Pair" in tdr_output[6]:
								status = tdr_output[8]
							else:
								status = tdr_output[7]
							length = tdr_output[2]
						
						# we throw the results for each line here
						complete_results += "," + length + "," + status
					else:
						continue
				# finally we've built the output that we can print
				output += "," + speed + complete_results
				print output
				
			# we sleep a little bit just in case the results haven't come in yet
			time.sleep(2)
	else:	# this only happens if we can't ping the device
		print row['Switch'] + "," + row['IP'] + ',down'


