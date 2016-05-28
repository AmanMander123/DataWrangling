#Audit the data from the OpenStreetMap file

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

#Assign file name to a variable
OSMFILE = "waterloo-region_canada.osm"

#Regular expression to be used to extract street type
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

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

#Define function to create a dictionary of unexpected street types
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

#Function to see if element attribute is a street name
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

#Check if element attribute is postal code
def is_postcode(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:postcode")

#Function to audit the street names and return a list of unexpected street names
def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
        elem.clear()
    osm_file.close()
    return street_types

#Function to update the street types based on the mapping as defined above
def update_name(name, mapping):
    m = street_type_re.search(name)
    if m not in expected:
        if m.group() in mapping.keys():
            name = re.sub(m.group(), mapping[m.group()], name)
    return name
    
#Function to update postal codes to include a space between the first and last 3 characters



#Function to audit postal codes and street types - update street types
def test():
    
    #Audit postal codes
    for event, elem in ET.iterparse(OSMFILE):        
        if is_postcode(elem):
            print elem.attrib['v']
 
    
    #Audit and update street types
    st_types = audit(OSMFILE)
    #pprint.pprint(dict(st_types))

    #Update street names
    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            #print name, "=>", better_name
            if name == "Fifth AVenue":
                assert better_name == "Fifth Avenue"
            if name == "Parkside Dr.":
                assert better_name == "Parkside Drive"

if __name__ == '__main__':
    test()