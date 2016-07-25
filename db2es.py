#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import unicode_literals, absolute_import

import time

from elasticsearch.helpers import scan
from elasticsearch.exceptions import NotFoundError

from oclubs.app import app
from oclubs.access import database, elasticsearch, done
from oclubs.objs import Activity, Club

clses = [Club, Activity]

with app.app_context():
    for cls in clses:
        db_ids = database.fetch_onecol(
            cls.table,
            cls.identifier,
            {}
        )
        db_ids = set(int(x) for x in db_ids)
        db_max = max(db_ids)

        try:
            es_ids = scan(
                elasticsearch.es,
                index='oclubs',
                doc_type=cls.table,
                size=10000000,
                query={
                    'query': {'match_all': {}},
                    'size': 10000,
                    'fields': ['_id']
                })
            es_ids = (d['_id'] for d in es_ids)
        except NotFoundError:
            es_ids = []

        es_ids = set(int(x) for x in es_ids)

        if es_ids:
            es_max = max(es_ids)
        else:
            es_max = 0

        max_id = max(db_max, es_max)

        cls_searchprops = [
            prop.name for prop in [
                getattr(cls, propname) for propname in dir(cls)
            ] if hasattr(prop, 'search') and prop.search
        ]

        for i in xrange(1, max_id + 1):
            time.sleep(0.01)

            if i in db_ids:
                obj = cls(i)

                db_data = {}
                for propname in cls_searchprops:
                    db_data[propname] = (
                        getattr(cls, propname).search(getattr(obj, propname)))

                if i in es_ids:
                    es_data = elasticsearch.get(cls.table, i)
                    if db_data == es_data:
                        print 'TYPE %s ID %d MATCH' % (cls.table, i)
                    else:
                        print 'UPDATED ES TYPE %s ID %d' % (cls.table, i)
                        elasticsearch.update(cls.table, i, db_data)
                else:
                    print 'CREATED ES TYPE %s ID %d' % (cls.table, i)
                    elasticsearch.create(cls.table, i, db_data)
            else:
                if i in es_ids:
                    print 'DELETED ES TYPE %s ID %d' % (cls.table, i)
                    elasticsearch.delete(cls.table, i)
                else:
                    print 'TYPE %s ID %d DOES NOT EXIST' % (cls.table, i)
                    pass

    done()
