import sys

infile = open(sys.argv[1])
outfile = open(sys.argv[2], 'w')
def split(s, delim=None):
    return [x for x in s.split(delim) if x]
done = False
for line in infile.readlines():
    if done:
        nline = line
    else:
	if 'RDAT_VERSION' in line:
	    if '0.24' in line:
		done = True
	    nline = 'RDAT_VERSION 0.24\n'
	elif 'ANNOTATION_DATA' in line or 'AREA_PEAK' in line or 'XSEL' in line:
	    line = line.replace('AREA_PEAK', 'REACTIVITY')
	    fields = split(line.strip(), delim=' ')
	    nline = fields[0]+':'+fields[1]+' '+' '.join(fields[2:][::-1]) + '\n'
	elif 'SEQPOS' in line or 'MUTPOS' in line:
	    fields = split(line.strip(), delim=' ')
	    nline = fields[0] + ' ' + ' '.join(fields[1:][::-1]) + '\n'
	else:
	    nline = line

    outfile.write(nline)

infile.close()
outfile.close()


