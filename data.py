#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script wrangles the data and transforms the OpenStreetMap data
into dictionaries that look like this:

{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}


- Only 2 types of top level tags are procssed: "node" and "way"
- All attributes of "node" and "way" are turned into regular key/value pairs, except:
    - attributes in the CREATED array should be added under a key "created"
    - attributes for latitude and longitude should be added to a "pos" array,
      for use in geospacial indexing. The values inside "pos" array are floats
      and not strings. 
- if the second level tag "k" value contains problematic characters, it is ignored
- if the second level tag "k" value starts with "addr:", it is added to a dictionary "address"
- if the second level tag "k" value does not start with "addr:", but contains ":", it is processed
  as a regular tag
- if there is a second ":" that separates the type/direction of a street,
  the tag is ignored, for example:

<tag k="addr:housenumber" v="5158"/>
<tag k="addr:street" v="North Lincoln Avenue"/>
<tag k="addr:street:name" v="Lincoln"/>
<tag k="addr:street:prefix" v="North"/>
<tag k="addr:street:type" v="Avenue"/>
<tag k="amenity" v="pharmacy"/>

  is turned into:

{...
"address": {
    "housenumber": 5158,
    "street": "North Lincoln Avenue"
}
"amenity": "pharmacy",
...
}

- for "way" specifically:

  <nd ref="305896090"/>
  <nd ref="1719825889"/>

is turned into
"node_refs": ["305896090", "1719825889"]
"""
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

#List of expected street types
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons","1","10","11","116","12","124","13","14","15","154","16",
           "17","18","2","20","21","22","24","3","30","32","34","4","45","5","51","6","7","8","86",
           "9","97","Baseline","Boardwalk", "Circle", "Close","Cove", "Crescent", "Crestway", "Cross",
           "Crossing","East","West","South","North","Estates","Gardens","Gate", "Grove", "Heights", "Highway",
           "Hill", "Hollow", "Line", "Walk", "Way"]

#Map of incorrect to correct street types
mapping = { "St": "Street",
            "St.": "Street",
            "Ave" : "Avenue",
            "Rd." : "Road",
            "Rd" : "Road",
            "AVenue" : "Avenue",
            "Cresent" : "Crescent",
            "Dr" : "Drive",
            "Dr." : "Drive",
            "N" : "North",
            "E" : "East",
            "S" : "South",
            "W" : "West",
            "road" : "Road",
            "g" : "",
            "canadatrust.com" : "",
            "45th" : "45"
            }

#Function to update the street types based on the mapping as defined above
def update_name(name, mapping):
    m = street_type_re.search(name)
    if m not in expected:
        if m.group() in mapping.keys():
            name = re.sub(m.group(), mapping[m.group()], name)
    return name

#Function to update the problematic nodes
def update(node, value, tag):
    key = value
    value = tag.attrib['v']
    if key.startswith('addr:'):
        if key.count(':') == 1:
            if 'address' not in node:
                node['address'] = {}
            if key == 'addr:street':
                value = update_name(value, mapping)
            if key == 'addr:postcode':
            	if not re.match(r'^[A-Z]\d[A-Z] \d[A-Z]\d$', value):
            		value = value[0:3] + ' ' + value[3:6]
            node['address'][key[5:]] = value
    return node


#Function to convert XML input to JSON output
def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        node['type'] = element.tag
        node['created'] = {}
        if "lat" in element.keys() and "lon" in element.keys():
            pos = [float(element.attrib["lat"]), float(element.attrib["lon"])]
            node["pos"] = pos
        for tag in element.iter():
            for key, value in tag.items():
                if key in CREATED:
                    node['created'][key] = value
                elif key == 'k' and not re.search(problemchars, value):
                    node = update(node, value, tag)
                elif key == 'ref':
                    if 'node_refs' not in node:
                        node['node_refs'] = []
                    node['node_refs'].append(value)
                elif key not in ['v', 'lat', 'lon']:
                    node[key] = value
        element.clear()
        return node
    else:
        return None


def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    data = process_map('waterloo-region_canada.osm', True)
    pprint.pprint(data[-1])

if __name__ == "__main__":
    test()