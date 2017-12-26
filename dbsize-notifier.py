import mysql.connector as mdb
import smtplib
import datetime

try:
    db = mdb.connect(host="localhost", user="", password="", database="")
    cursor = db.cursor()
    date = datetime.datetime.now()
    current = str(date.year) + "-" + str(date.month) + "-" + str(date.day)

    query = """
        SELECT 
            table_schema "DB Name", 
            Round(Sum(data_length + index_length) / 1024 / 1024, 1) "DB Size in MB"  
        FROM   
            information_schema.tables 
        WHERE 
            table_schema="news"
        GROUP BY 
            table_schema;
    """
    cursor.execute(query)
    resultString = ''
    for row in cursor:
        resultString = row[0] + " Database | " + str(row[1]) + "MB\n"

    resultString = resultString + "\nPublication Date | Total\n"

    query = """
        select _pubdate, count(*) from news where added_on = "{}" group by _pubdate;
    """.format(current)

    cursor.execute(query)
    for row in cursor:
        resultString = resultString + str(row[0]) + " | " + str(row[1]) + "\n"

    query = """
        select s.src_name, count(*) from news n, news_sources s where n.src_id = s.src_id and n.added_on="{}" group by s.src_name;
    """
    cursor.execute(query.format(current))

    resultString = resultString + "\nSource                      | Total\n"
    for row in cursor:
        resultString = resultString + str(row[0]) + " | " + str(row[1]) + "\n"    

    sender = 'cronnews@market.com'
    receivers = ['user@gmail.com']

    msg = "\r\n".join([
        "From: user_me@gmail.com",
        "To: user_you@gmail.com",
        "Subject: News Database Params | " + current,
        "",
        "{}".format(resultString)
    ])

    try:
        server = smtplib.SMTP(host='smtp.gmail.com', port=587)
        server.ehlo()
        server.starttls()
        server.login('sample@gmail.com', 'sample')
        server.sendmail(sender, receivers, msg)         
        print "Successfully sent email"
        server.close()
    except Exception as e:
        print "Error: unable to send email", e
except Exception as e:
    print e
finally:
    db.close()
