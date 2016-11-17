import re

def extract(keyChain, node, fallback):

    if keyChain is None:
        obj = fallback

    else:
        if isinstance(keyChain, basestring):
            keyChain = keyChain.split(".");

        obj = None

        if node is not None:
            if len(keyChain) == 0:
                obj = node
            else:
                newKeyChain = keyChain[1:]
                if len(newKeyChain) == 0:
                    if isinstance(keyChain[0], basestring) and keyChain[0].lower() == "length":
                        if isinstance(node, list):
                            obj = len(node)
                        else:
                            obj = node.get("length", 0)

            if (obj is None) and (node is not None):
                if isinstance(node, list):
                    index = int(keyChain[0]) if isinstance(keyChain[0], basestring) else keyChain[0]
                    obj = extract(newKeyChain, node[index], fallback)
                else:
                    obj = extract(newKeyChain, node.get(""+keyChain[0]), fallback)
        else:
            obj = fallback

    return obj


def getRequestParameters(request, name, fallback):
    value = None
    params = request.GET.lists()
    if params:
        for k, v in params:
            if k == name:
                value = v
                break

    if value == None:
        value = fallback
    return value


def getRequestParameter(request, name, fallback):
    values = getRequestParameters(request, name, None)
    if values:
        if values and len(values) == 1:
            return values[0]
        else:
            return fallback
    else:
        return fallback


def getRequestParameterAsInteger(request, name, fallback):
    values = getRequestParameters(request, name, None)
    if values:
        if values and len(values) == 1:
            return int(values[0]) if isinstance(values[0], basestring) else values[0]
        else:
            return fallback
    else:
        return fallback


def getRequestParameterAsFloat(request, name, fallback):
    values = getRequestParameters(request, name, None)
    if values:
        if values and len(values) == 1:
            return float(values[0]) if isinstance(values[0], basestring) else values[0]
        else:
            return fallback
    else:
        return fallback

def getRequestParameterAsList(request, name, fallback):
    values = getRequestParameters(request, name, None)
    if values:
        if values and len(values) == 1:
            return values[0].split(",") if isinstance(values[0], basestring) else values[0]
        else:
            return fallback
    else:
        return fallback


def testValue(obj=None, path=None, operand=None, valueType=None, value_test=None, value_min=None, value_max=None):

    if operand == "=" or operand == u"=":
        if valueType == "int" or valueType == "integer" or valueType == u"int" or valueType == u"integer":
            return extract(unicode(path), obj, None) == int(value_test)
        elif valueType == "double" or valueType == "float" or valueType == u"double" or valueType == u"float":
            return extract(unicode(path), obj, None) == float(value_test)
        else:
            return extract(unicode(path), obj, None) == value_test
    elif operand == ">=" or operand == u">=":
        if valueType == "int" or valueType == "integer" or valueType == u"int" or valueType == u"integer":
            return extract(unicode(path), obj, None) >= int(value_test)
        elif valueType == "double" or valueType == "float" or valueType == u"double" or valueType == u"float":
            return extract(unicode(path), obj, None) >= float(value_test)
        else:
            return extract(unicode(path), obj, None) == value_test
    elif operand == "between" or operand == "btwn":
        if valueType == "int" or valueType == "integer" or valueType == u"int" or valueType == u"integer":
            try:
                value = extract(unicode(path), obj, None)
                return value >= int(value_min) and value <= int(value_max)
            except:
                return False
        elif valueType == "double" or valueType == "float" or valueType == u"double" or valueType == u"float":
            try:
                value = extract(unicode(path), obj, None)
                return value >= float(value_min) and value <= float(value_max)
            except:
                return False
        else:
            return False
    else:
        return True

def parseFilter(x):
    m = re.match("^([A-Za-z0-9_.]+)(\\s*)([>][=]|[<][=]|[=><])(\\s*)(.+)$", x, re.MULTILINE|re.IGNORECASE)
    if m:
        return {'path': m.group(1), 'operand': m.group(3), 'value': m.group(5)}
    if m:
        return {'path': m.group(1), 'operand': m.group(3), 'value': m.group(5)}
    else:
        m = re.match("^([A-Za-z0-9_.]+)(\\s*)(between|btwn)(\\s*)([0-9.]+)(\\s*)(and)(\\s*)([0-9.]+)$", x, re.MULTILINE|re.IGNORECASE)
        if m:
            return {'path': m.group(1), 'operand': m.group(3), 'min': m.group(5), 'max': m.group(9)}
        else:
            return None

def grep(**kwargs):

    obj = kwargs.get('obj')
    root = kwargs.get('root')
    attributes = kwargs.get('attributes')
    filters = kwargs.get('filters')

    if obj is None:
        return None

    print "grep"
    for k, v in kwargs.iteritems():
        if k != "obj":
            print k, ":", v,"\n------------\n"
    print "#############################"

    attribute_map = {}
    for path in [x['path'] for x in attributes if x.get('path') and (x.get('type') == "integer" or x.get('type') == "int")]:
        attribute_map[path] = "int"
    for path in [x['path'] for x in attributes if x.get('path') and (x.get('type') == "double" or x.get('type') == "float")]:
        attribute_map[path] = "float"

    if filters is None:
        return obj
    else:
        if root is None:
            for f in filters:
                filtered = []
                if isinstance(f, basestring):
                    f2 = parseFilter(f)
                    if f2:
                        print "f2:", f2
                        for item in obj:
                            #print "item:", item
                            #print "value type: ", attribute_map.get(f2["path"], "string")
                            include = testValue(
                                obj=item,
                                path=f2['path'],
                                value_test=f2.get('value'),
                                value_min=f2.get('min'),
                                value_max=f2.get('max'),
                                operand=f2['operand'],
                                valueType=attribute_map.get(f2["path"], "string"))
                            if include:
                                filtered.append(item)

                else:
                    for item in obj:
                        if extract(f['path'], item, None) == f['value']:
                            filtered.append(item)
                obj = filtered
        else:
            for f in filters:
                items = extract(root, obj, None)
                if items is not None:
                    filtered = []
                    if isinstance(f, basestring):
                        f2 = parseFilter(f)
                        if f2:
                            for item in items:
                                include = testValue(
                                    obj=item,
                                    path=f2['path'],
                                    value_test=f2.get('value'),
                                    value_min=f2.get('min'),
                                    value_max=f2.get('max'),
                                    operand=f2['operand'],
                                    valueType=attribute_map.get(f2["path"], "string"))
                                if include:
                                    filtered.append(item)
                    else:
                        for item in items:
                            if extract(f['path'], item, None) == f['value']:
                                filtered.append(item)

                    obj[root] = filtered

        return obj

def reduceValue(r, value, feature=None):
    if r:
        op = r.get('op') or r.get('operation')
        if op == "sum":
            g = r.get('grep')
            if g:
                rows = grep(
                    obj=value,
                    root=None,
                    attributes=r.get('attributes'),
                    filters=g
                )
                return sum([extract(r['path'], x, 0) for x in rows])
            else:
                return sum([extract(r['path'], x, 0) for x in value])

        elif op == "profile":
            profiles = [extract(path, feature, None) for path in r['paths']]
            if len([x for x in profiles if (x is not None)]) > 0:
                modifier = sum([x for x in profiles if x is not None])
                if modifier != 0:
                    denominator = extract("denominator", r, 1)
                    return (value * modifier) / denominator
                else:
                    return 0
            else:
                return value
        else:
            return value
    else:
        return value


    #subrows = grep(
    #    obj=row[i],
    #    root=None,
    #    attributes=r.get('attributes'),
    #    filters=r.get('grep')
    #)
    #print "Subrows:"
    #for subrow in subrows:
    #    print subrow
    #print ""
    #row[i] = sum([extract(r['path'], x, 0) for x in subrows])


class GeoDashMetadataWriter():

    def __init__(self, output, dataset, fallback=""):
        self.output = output
        self.dataset = dataset
        self.fallback = fallback
        self.quote = u'"'
        self.newline = u"\n"

    def write_line(self, line):
        self.output.write(line+"\n")

    def write_lines(self, lines):
        if lines:
            for line in lines:
                self.output.write(line+"\n")

    def write_newlines(self, lines=1):
        for i in range(lines):
            self.output.write("\n")

    def write_break(self, newline=False, character="-", count=28):
        self.write_line("".join([character for i in range(count)]))
        if newline:
            self.write_line("");

    def write_attributes(self):
        for attribute in self.dataset['attributes']:
            self.write_line(attribute.get('label')+" | "+attribute.get('type', 'string'))
            self.write_line(attribute.get('description', 'No description given.'))
            self.write_newlines(1)
            self.write_break()


class GeoDashDictWriter():

    def __init__(self, output, dataset, fallback=""):
        self.output = output
        self.dataset = dataset
        self.fallback = fallback
        self.delimiter = u","
        self.quote = u'"'
        self.newline = u"\n"

    def _reduce(self, row, feature=None):
        for i in range(len(self.dataset['attributes'])):
            for r in extract('reduce', self.dataset['attributes'][i], []):
                row[i] = reduceValue(r, row[i], feature=feature)
        return row

    def _process_attr(self, attr, obj):
        if 'value' in attr:
            return attr.get('value')
        else:
            return extract(attr.get('path'), obj, self.fallback)

    def writeheader(self):
        self.output = self.output + self.delimiter.join([self.quote+x['label']+self.quote for x in self.dataset['attributes']]) + self.newline

    def writerow(self, rowdict):
        row = [self._process_attr(x, rowdict) for x in self.dataset['attributes']]
        #
        row = self._reduce(row, feature=rowdict)
        row = [unicode(x) for x in row]
        row = [x.replace('"','""') for x in row]
        #
        self.output = self.output + self.delimiter.join([self.quote+x+self.quote for x in row]) + self.newline

    def writerows(self, rowdicts):
        rows = []
        for rowdict in rowdicts:
            row = [self._process_attr(x, rowdict) for x in self.dataset['attributes']]
            #
            row = self._reduce(row, feature=rowdict)
            row = [unicode(x) for x in row]
            row = [x.replace('"','""') for x in row]
            #
            rows.append(row)

        for row in rows:
            self.output = self.output + self.delimiter.join([self.quote+x+self.quote for x in row]) + self.newline

    def getvalue(self):
        return self.output
