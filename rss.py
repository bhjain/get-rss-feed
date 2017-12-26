import requests
import xml.etree.ElementTree as ET
import re
from dateutil import parser

def feed_read(url):
    r = requests.get(url)
    if r.status_code == 200:
        try:
            xmltree = ET.fromstring(r.text.encode(encoding='UTF-8'))
            results = []
            for elem in xmltree.iter():
                if (elem.tag == "item"):
                    item = dict()
                    for child in elem.iter():
                        if child.tag == "pubdate" or child.tag == "pubDate":
                            item['pubdate'] = parser.parse(child.text).strftime("%Y-%m-%d")
                        elif child.tag == "item":
                            pass
                        elif child.tag == "image" or child.tag == "Image":
                            item['image'] = child.text.encode(encoding='UTF-8')
                            print item['image']
                        else:
                            try:
                                item[child.tag] = re.sub("'", "", child.text.encode(encoding='UTF-8').strip())
                            except Exception as e:
                                print "Error: ", child.tag

                    results.append(item)

            return results
        except Exception:
            return url