from simplejson import JSONEncoder

class RMDBJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Publication):
            jdict = {}
            for att in obj.__dict__:
                if att[0] != '_':
                    jdict[att] = obj.__dict__[att]
            return jdict
        if isinstance(obj, Organism):
            jdict = {}
            for att in obj.__dict__:
                if att[0] != '_' and att[0] != 'id':
                    jdict[att.replace('taxonomy_id', 'id')] = obj.__dict__[att]
            return jdict

        if isinstance(obj, RMDBEntry):
            entrydict = {}
            entrydict['rmdb_id'] = obj.rmdb_id
            entrydict['comments'] = obj.comments
            if obj.publication:
                entrydict['publication'] = self.default(obj.publication)
            else:
                entrydict['publication'] = {}
            entrydict['authors'] = obj.authors.split(',')
            entrydict['description'] = obj.description
            entrydict['type'] = obj.type
            entrydict['revision_status'] = obj.revision_status
            entrydict['creation_date'] = str(obj.creation_date)
            entrydict['from_eterna'] = obj.from_eterna
            if obj.pdb_entries:
                entrydict['pdb_entries'] = obj.pdb_entries.split(',')
            else:
                entrydict['pdb_entries'] = []
            if 'constructs' in obj.__dict__:
                entrydict['constructs'] = [self.default(c) for c in obj.constructs]
            if 'annotations' in obj.__dict__:
                entrydict['annotations'] = dict([self.default(a) for a in obj.annotations])
            return entrydict

        if isinstance(obj, DataAnnotation) or isinstance(obj, EntryAnnotation):
            return (obj.name, obj.value)

        if isinstance(obj, ConstructSection):
            constructdict = {}
            for att in obj.__dict__:
                if att == 'entry' or att[0] == '_':
                    continue
                elif att == 'annotations':
                    datadict['annotations'] = dict([self.default(a) for a in obj.annotations])
                elif att == 'datas':
                    constructdict['data_sections'] = [self.default(d) for d in obj.datas]
                elif att in ['mutpos', 'seqpos', 'xsel']:
                    if len(obj.__dict__[att]) > 0:
                        constructdict[att] = [i for i in obj.__dict__[att].strip('[]').split(',')]
                elif att == 'offset':
                    constructdict[att] = int(obj.offset)
                else:
                    constructdict[att] = obj.__dict__[att]
            return constructdict

        if isinstance(obj, DataSection):
            datadict = {}
            for att in obj.__dict__:
                if att == 'construct_section' or att[0] == '_':
                    continue
                elif att == 'annotations':
                    datadict['annotations'] = dict([self.default(a) for a in obj.annotations])
                elif att in ['seqpos', 'xsel', 'values', 'errors', 'error', 'trace', 'reads']:
                    if obj.__dict__[att] is not None and len(obj.__dict__[att]) > 0:
                        datadict[att] = [float(i) for i in obj.__dict__[att].strip('[]').split(',')]
                else:
                    datadict[att] = obj.__dict__[att]

            return datadict
        return JSONEncoder().encode(obj)