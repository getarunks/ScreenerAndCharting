arr = []
with open('2.txt') as inf:
	for line in inf:
		parts = line.split()
		arr.append(parts[0])

with open('columnOutput.txt', 'w') as op:
	op.write(str(arr).translate(None, "'"))
print len(arr)
print str(arr).translate(None, "'")
