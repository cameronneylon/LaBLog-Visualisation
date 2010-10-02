# A quick and dirty script for converting a lablog xml dump into a json format and
# from there on to GUESS for importing into Gephi
#
# TODO: 
# 1. Collect information on links to data elements as well as posts.
# 2. Sort out extra post elements like permalinks and metadata
# 3. Capture links to external web pages
# 4. Grab links to other blogs on the same server to obtain titles etc.

from xml.etree import ElementTree as ET
import re
import simplejson

infile = 'blogdump.xml'
jsonfile = 'blogdump.json'
guessfile = 'blogdump.gdf'

tree = ET.parse(infile)
root = tree.getroot()

bloglinks = re.compile('(\\[blog\\])' + '(\\d+)' + 
                       '(\\[\\/blog\\])', re.IGNORECASE|re.DOTALL)

f = open(jsonfile, 'w')

dumplist = []

for post in root.getiterator('post'):
    postdict = {}
    postdict['title'] = post.find('title').text
    postdict['id'] = post.find('id').text
    postdict['section'] = post.find('section').text
    postdict['author'] = post.find('author').text
    postdict['datestamp'] = post.find('datestamp').text
    postdict['timestamp'] = post.find('timestamp').text
    postdict['content'] = {'bbcode': post.find('content').text,
                           'html'  : post.find('html').text}

    postdict['internal-links'] = []
    # Search through content for [blog]###[/blog] and create iterator
    bloglinkslist = bloglinks.finditer(post.find('content').text)
    for link in bloglinkslist:
        # For each link grab the ID and append to list of links
        postdict['internal-links'].append(link.group(2))
        
    # postdict['permalink'] = post.find('permalink').text

    dumplist.append(postdict)

f.write(simplejson.dumps(dumplist))
f.close

f2 = open(guessfile, 'w')

#label is a reserved word used to display node labels
f2.write('nodedef> name, label STRING, section VARCHAR\n')

nodelist = ''
nodetrack = []
edgelist = ''

for post in dumplist:
    nodelist += ('id' + post['id'] +',' + post['title'] + ','
                    + post['section'] + '\n')
    nodetrack.append(post['id'])

for post in dumplist:
    for link in post['internal-links']:
        edgelist += 'id' + post['id'] + ',id' + link + '\n'
        if nodetrack.count(link) == 0:
            nodelist += 'id' + link +',external,unknown\n'
    
f2.write(nodelist)
f2.write('edgedef>node1,node2\n')
f2.write(edgelist)
f2.close

