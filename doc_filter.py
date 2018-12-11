#!/usr/bin/python
# -*- coding: UTF-8 -*-

import pymysql
from textblob import TextBlob
from math import sqrt
from numpy import asarray

department = 'Internal Medicine'
lat = 72
lng = 49
startTime = '2018-12-10 10:00:00'
endTime = '2018-12-10 18:00:00'
language = 'Chinese'


def sentiment_analyse(review_list, mark_list):

    t = 0
    n = 0
    for (r, m) in zip(review_list, mark_list):
            blob = TextBlob(r)
            b = 5 * blob.sentiment.polarity + 5
            m = (m * b) / (0.7 * b + 0.3 * m)
            t = m + t
            n = n + 1
    if t == 0:
        return 0
    else:
        return t / n


def total_mark(review_list, mark_list):

    tm = []
    i = 0
    while i < len(mark_list):
        tm.append(sentiment_analyse(review_list[i], mark_list[i]))
        i = i + 1
    return tm


def geo_distance(lng1, lat1, lng2, lat2):
        d = []

        for (ln2, la2) in zip(lng2, lat2):
            dis = sqrt(pow((ln2 - lng1), 2)+pow((la2 - lat1), 2))
            d.append(dis)
        return d


def m_dis(d, tm):
    i = 0
    md = []

    for (d[i], tm[i]) in zip(d, tm):
        dis = sqrt(pow(d[i], 2) + pow(tm[i] - 10, 2))
        md.append(dis)
        i = i + 1
    return md


def first_filter():

    sql_first_filter = "select * from doctorentity " \
          " where " + "language = \'" + language + '\'' + \
          " and " + "department = \'" + department + '\'' + \
          " and " + "lat >= " + str(lat-3) + \
          " and " + "lat <= " + str(lat+3) + \
          " and " + "lng <= " + str(lng+3) + \
          " and " + "lng >= " + str(lng-3) + \
          " and " + "startTime <=" + '\'' + startTime + '\'' + \
          " and " + "endTime >= " + '\'' + endTime + '\''

    doc_id_list = []

    sql_db = pymysql.connect('localhost', 'root', 'database password', 'database name')

    try:
        sql_cursor = sql_db.cursor()
        sql_cursor.execute(sql_first_filter)
        sql_result = sql_cursor.fetchall()
        sql_db.commit()

        # get doc_id list from first filter
        for sql_row in sql_result:
            doc_id_list.append(sql_row[0])
    except:
        print("first filter failed")

    # create mark_list[[]] to store the data
    mark_list = [([] * len(doc_id_list)) for p in range(len(doc_id_list))]
    review_list = [([] * len(doc_id_list)) for p in range(len(doc_id_list))]
    doc_lng_list = []
    doc_lat_list = []

    for i in range(len(doc_id_list)):

        sql_second_filter = 'select mark, review from userreviewentity where docid=\'' + doc_id_list[i] + '\''
        sql_second_filter1 = 'select lat, lng from doctorentity where docid=\'' + doc_id_list[i] + '\''

        try:
            sql_cursor.execute(sql_second_filter)
            sql_result = sql_cursor.fetchall()
            sql_db.commit()

            for sql_row in sql_result:
                mark_list[i].append(sql_row[0])
                review_list[i].append(sql_row[1])

            sql_cursor.execute(sql_second_filter1)
            sql_result = sql_cursor.fetchall()
            sql_db.commit()

            for sql_row in sql_result:
                doc_lat_list.append(sql_row[0])
                doc_lng_list.append(sql_row[1])

        except:
            print('second filter failed')

        # 100 [8,9] [good, fantastic]
        # 101 [9] [good]
    tm = total_mark(review_list, mark_list)
    d = geo_distance(lng, lat, doc_lng_list, doc_lat_list)
    md = m_dis(d, tm)
    x = list(zip(doc_id_list, md))
    print(asarray(sorted(x, key=lambda x: x[1])))


def main():
    first_filter()


if __name__ == '__main__':
    main()
