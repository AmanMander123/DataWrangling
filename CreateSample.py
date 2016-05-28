{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "#!/usr/bin/env python\n",
    "# -*- coding: utf-8 -*-\n",
    "\n",
    "import xml.etree.ElementTree as ET  # Use cElementTree or lxml if too slow\n",
    "\n",
    "OSM_FILE = \"waterloo-region_canada.osm\"  # Replace this with your osm file\n",
    "SAMPLE_FILE = \"sample.osm\"\n",
    "\n",
    "k = 20 # Parameter: take every k-th top level element\n",
    "\n",
    "def get_element(osm_file, tags=('node', 'way', 'relation')):\n",
    "    \"\"\"Yield element if it is the right type of tag\n",
    "\n",
    "    Reference:\n",
    "    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python\n",
    "    \"\"\"\n",
    "    context = iter(ET.iterparse(osm_file, events=('start', 'end')))\n",
    "    _, root = next(context)\n",
    "    for event, elem in context:\n",
    "        if event == 'end' and elem.tag in tags:\n",
    "            yield elem\n",
    "            root.clear()\n",
    "\n",
    "\n",
    "with open(SAMPLE_FILE, 'wb') as output:\n",
    "    output.write('<?xml version=\"1.0\" encoding=\"UTF-8\"?>\\n')\n",
    "    output.write('<osm>\\n  ')\n",
    "\n",
    "    # Write every kth top level element\n",
    "    for i, element in enumerate(get_element(OSM_FILE)):\n",
    "        if i % k == 0:\n",
    "            output.write(ET.tostring(element, encoding='utf-8'))\n",
    "\n",
    "    output.write('</osm>')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 2",
   "language": "python",
   "name": "python2"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 2
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython2",
   "version": "2.7.11"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 0
}
