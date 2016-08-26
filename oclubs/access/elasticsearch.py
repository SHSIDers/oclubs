#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import, unicode_literals

import re

from elasticsearch import Elasticsearch

from oclubs.access.delay import delayed_func

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])


@delayed_func
def create(doc_type, doc_id, data):
    return es.create(
        index='oclubs',
        doc_type=doc_type,
        body=data,
        id=doc_id
    )['created']


@delayed_func
def delete(doc_type, doc_id):
    return es.delete(
        index='oclubs',
        doc_type=doc_type,
        id=doc_id,
    )['found']


def get(doc_type, doc_id, fields=True):
    ret = es.get(
        index='oclubs',
        doc_type=doc_type,
        id=doc_id,
        _source=fields
    )

    if fields is not False:
        return ret['_source']
    else:
        return ret['found']


@delayed_func
def update(doc_type, doc_id, data):
    return es.update(
        index='oclubs',
        doc_type=doc_type,
        id=doc_id,
        body={'doc': data}
    )


def _search(querystr, doc_type, fields, offset=0, size=10,
            do_suggest=True, _count_instead=False):
    body = {
        'query': {
            'simple_query_string': {
                'query': querystr,
                'fields': fields,
                'default_operator': 'AND'
            },
        },
        'highlight': {
            'encoder': 'html',
            'pre_tags': ['<strong>'],
            'post_tags': ['</strong>'],
            'fields': {'*': {}}
        },
        'size': size,
        'from': offset
    }

    if _count_instead:
        return es.count(
            index='oclubs',
            doc_type=doc_type,
            body={'query': body['query']}
        )['count']

    if do_suggest:
        suggest = {'text': querystr}

        for field in fields:
            suggest[field] = {
                'term': {
                    'size': 1,
                    'field': field,
                    'suggest_mode': 'popular'
                }
            }

        body['suggest'] = suggest

    return es.search(
        index='oclubs',
        doc_type=doc_type,
        body=body
    )


def search(querystr, *args, **kwargs):
    ret = {
        'instead': None,
        'results': [],
        'count': 0
    }

    if not querystr:
        return ret

    result = _search(querystr, do_suggest=True, *args, **kwargs)
    if result['hits']['hits']:
        ret['results'] = result['hits']['hits']
        ret['count'] = _search(querystr, _count_instead=True, *args, **kwargs)
        return ret

    suggest_table = {}

    for field, suggestlist in result['suggest'].items():
        for worddict in suggestlist:
            word = worddict['text']
            for option in worddict['options']:
                score, newword = option['score'], option['text']

                if word in suggest_table and score < suggest_table[word][0]:
                    continue

                suggest_table[word] = score, newword

    if not suggest_table:
        return ret

    for word, (_, newword) in suggest_table.items():
        querystr = re.sub(r'\b%s\b' % re.escape(word), newword, querystr)

    result = _search(querystr, do_suggest=False, *args, **kwargs)
    if result['hits']['hits']:
        ret['results'] = result['hits']['hits']
        ret['instead'] = querystr
        ret['count'] = _search(querystr, _count_instead=True, *args, **kwargs)

    return ret
