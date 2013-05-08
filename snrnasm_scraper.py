import urllib2
from xml.dom import minidom
import array
from shutil import copy
from time import strftime
from os import remove

def parse(target):
	# start the log
	rec('log','%s:Downloading rss feed\n'%strftime('%Y %m %d %X'))
	# save the xml so it can be edited
	rssfeed = urllib2.urlopen("http://rmdb.stanford.edu/site_media/rss/isatab.xml")
	s = rssfeed.read()
	rssfeed.close()
	s = s.replace('&', '&amp;')
	rec('xml',s)
	feed = minidom.parse('/Applications/MAMP/htdocs/snrnasm/rmdb_xml.txt')
	snrnasmdata = True
	title = False; lasttitle = False
	link = False;
	links = []
	seen = []
	
	# go through each "item" in the feed
	for item in feed.getElementsByTagName('item'):
		for node in item.childNodes:
			if node.nodeType == 1 and node.hasChildNodes() == True:
				# get the info from each item and add it to a list of links
				snrnasmdata = check_node(node.nodeName, node.childNodes.item(0).nodeValue)

				if isinstance(snrnasmdata, unicode) and snrnasmdata[0:4] == 'link':
					link = snrnasmdata[5:]; lasttitle = title
				elif isinstance(snrnasmdata, unicode) and snrnasmdata[0:5] == 'title':
					title = snrnasmdata[5:]
				elif isinstance(snrnasmdata, unicode) and snrnasmdata[0:4] == 'desc':
					desc = snrnasmdata[5:]
			# when moving to the next node, make the link for the previous one ignoring duplicates
			if node.nodeName == 'description':
				if link not in seen:
					seen.append('%s'%link)
					try:
						links.append("<a href='%s'>%s:</a> %s\n"%(link, lasttitle, desc))
						del desc
					except: links.append("<a href='%s'>%s</a>\n"%(link, title))
				
	# sort the links
	links = sorted(set(links))
	addlinks(links) # send all of the links found to addlinks() to be written to the file
	# close the log
	rec('log','%s =========================================================='%strftime('%Y %m %d %X'))
	
def check_node(label, value):
	
	if label == 'title':
		# set the value for the title of the link
		return 'title %s'%value
	
	if label == 'link':
		return 'link %s'%value
		
	if label == 'description':
		return "desc %s"%value
				
	else: return # skip the fields other than 'link' 'title' and 'description'
	
# def numerical(date):
	day = date[0:2]
	months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
	month = months.index(date[3:6])
	if len(str(month))<2:
		month = '0%d'%month
	year = date[7:11]
	time = date[12:17]
	
	dat = '%s%s%s'%(year,month,day)
	return('%s %s')%(dat,time)
	
def addlinks(links):
	# backup the file before writing the links, then load from the template
	copy('/Applications/MAMP/htdocs/snrnasm/browse.html', '/Applications/MAMP/htdocs/snrnasm/browse.old')
	copy('/Applications/MAMP/htdocs/snrnasm/template.html', '/Applications/MAMP/htdocs/snrnasm/browse.html')
	
	with open("/Applications/MAMP/htdocs/snrnasm/browse.html", 'a') as newfile:
		
		for link in links:
			newfile.write('%s<br>\n'%link)
			rec('log',link)
				
		# end the file
		newfile.write('\n</body>\n</html>')

def rec(loc,msg):
	locs = {'log':'/Applications/MAMP/htdocs/snrnasm/log.txt','xml':'/Applications/MAMP/htdocs/snrnasm/rmdb_xml.txt'}
	loc = locs[loc]
	with open(loc, 'a') as output:
		output.write(msg)
	return 

try: parse('http://rmdb.stanford.edu/site_media/rss/isatab.xml')
finally: remove('/Applications/MAMP/htdocs/snrnasm/rmdb_xml.txt')