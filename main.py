import ConfigParser
import mysql.connector as mdb
import datetime

from rss import feed_read

try:
	db = mdb.connect(host="localhost", user="", password="", database="")
	cursor = db.cursor()

	config = ConfigParser.ConfigParser()
	config.read('./rss-readers.cfg')
	date = datetime.datetime.now()
	current = str(date.year) + "-" + str(date.month) + "-" + str(date.day)

	query = """
	    INSERT INTO
	        news (_title, _link, _pubdate, _desc, src_id, type_id, _image, added_on)
	    VALUES
	        ('{0}', '{1}', '{2}', '{3}',
	        (SELECT src_id FROM news_sources WHERE src_name="{4}"),
	        (SELECT type_id FROM news_types WHERE type_name="{5}"),
	        '{6}', '{7}');
	"""

	for section in config.sections():
		cursor.execute("SELECT * FROM news_sources WHERE src_name = '{}'".format(section))
		if (not len(cursor.fetchall())):
			cursor.execute("INSERT INTO news_sources(src_name) VALUES('{}')".format(section))
			db.commit()
			print "Inserting {}".format(section)

		for name,value in config.items(section):
			cursor.execute("SELECT * FROM news_types WHERE type_name = '{}'".format(name))
			if (not len(cursor.fetchall())):
				cursor.execute("INSERT INTO news_types(type_name) VALUES('{}')".format(name))
				db.commit()
				print "Inserting {}".format(name)

			cnt = 1
			for element in feed_read(value):
				try:
					pubdate = element['pubdate'] if 'pubdate' in element else ''
					image = element['image'] if 'image' in element else ''

					pubdatetime = datetime.datetime.strptime(pubdate, '%Y-%m-%d')
					pdt = str(pubdatetime.year) + "-" + str(pubdatetime.month) + "-" + str(pubdatetime.day)
					if current == pdt:
						cursor.execute(query.format(element['title'], element['link'], pubdate, element['description'], section, name, image, current))
						db.commit()
						print "Inserting news article {} into {} {} from {}".format(cnt, section, name, value)	
					cnt = cnt + 1
				except mdb.Error as e:
					print e
				except Exception as e:
					print "=>", e, element
except mdb.Error as e:
    print e
finally:
	db.close()
