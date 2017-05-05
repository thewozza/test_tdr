with open ("tdr_output.txt", "r") as inputfile:
	show_tdr_results = inputfile.read()
	
print show_tdr_results

intElement = ["Gi3/0/23"]
output = intElement[0]
complete_results = ""

for tdr_output in show_tdr_results.split("\n"):
	if "-" in tdr_output:
		tdr_output = tdr_output.rstrip().lstrip()
		tdr_output =  " ".join(tdr_output.split())
		tdr_output = tdr_output.split(" ")
		try:
			tdr_output[1]
		except IndexError:
			continue
		if "---------" in tdr_output[0]:
			continue
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
		complete_results += " " + length + " " + status
			
	else:
		continue

output += " " + speed + complete_results

print output