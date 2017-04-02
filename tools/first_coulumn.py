arr = []
with open('2') as inf:
	for line in inf:
		parts = line.split()
		arr.append(parts[0])

print len(arr)
print str(arr).translate(None, "'")
