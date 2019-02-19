import xml.etree.ElementTree as ET

tree = ET.parse('7daylimited.xml')

root = tree.getroot()

print(root.tag)

for tag in root.findall('channel'):
    print(tag.attrib['id'])
    print(tag.find('display-name').text)
