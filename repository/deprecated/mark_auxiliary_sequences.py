from rmdb.repository.settings import *
from rmdb import settings
from django.core.management  import setup_environ
setup_environ(settings)
from django.template.defaultfilters import slugify
from rmdb.repository.models import *
import pdb


constructs = ConstructSection.objects.all()

auxiliary_seqs = ['GGAACAAACAAAACA','GGCCAAAACAACG','GAAAGGAAAGGGAAAGAA','GGAAAAA','GGACAGAGA','AAACCAAAGAAACAACAACAACAAC','AAAACAAAACAAAGAAACAACAACAACAAC','AAAACACAACAAAGAAACAACAACAACAAC']
for c in constructs:
    nseq = c.sequence
    for seq in auxiliary_seqs:
	nseq = nseq.replace(seq, seq.lower())
    c.sequence = nseq
    c.save()

entries = RMDBEntry.objects.all()
for e in entries:
    if 'RNASEP_SHP' not in e.rmdb_id and 'ETE' not in e.rmdb_id:
	e.comments += ' Auxiliary sequences are marked in lowercase.'
        e.save()
