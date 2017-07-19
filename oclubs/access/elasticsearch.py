#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

"""
Module to access Elasticsearch search engine.

This module has delayed functions to create/update/delete documents on the
engine, and to search within all the documents.
"""

from __future__ import absolute_import, unicode_literals

import re

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError

from oclubs.access.delay import delayed_func

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])


@delayed_func
def create(doc_type, doc_id, data):
    """
    Create an Elasticsearch document.

    :param basestring doc_type: document type
    :param doc_id: document id, will be converted into basestring
    :param dict data: new document data
    """
    return es.create(
        index='oclubs',
        doc_type=doc_type,
        body=data,
        id=doc_id
    )['created']


@delayed_func
def delete(doc_type, doc_id):
    """
    Delete an Elasticsearch document.

    :param basestring doc_type: document type
    :param doc_id: document id, will be converted into basestring
    """
    return es.delete(
        index='oclubs',
        doc_type=doc_type,
        id=doc_id,
    )['found']


def get(doc_type, doc_id, fields=True):
    """
    Get an Elasticsearch document.

    :param basestring doc_type: document type
    :param doc_id: document id, will be converted into basestring
    :param fields: if ``False``, returns whether the document is found as bool;
        if ``True``, returns the document dict; if list of string, returns the
        document dict with only the specified fields.
    :rtype: dict or bool
    """
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
    """
    Update an Elasticsearch document.

    :param basestring doc_type: document type
    :param doc_id: document id, will be converted into basestring
    :param dict data: new document data
    """
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
    """
    Search for Elasticsearch documents.

    :param basestring querystr: query string
    :param basestring doc_type: document type
    :param doc_id: document id, will be converted into basestring
    :param fields: fields to search on
    :type fields: list of basestring
    :param int offset: search offset
    :param int size: search size
    :returns:
        - 'instead' (basestring or None): the alternative search query
        - 'results' (list of dict): list of documents
        - 'count' (int): the number of all matching documents
    :rtype: dict
    """
    ret = {
        'instead': None,
        'results': [],
        'count': 0
    }

    if not querystr:
        return ret

    try:
        result = _search(querystr, do_suggest=True, *args, **kwargs)
    except NotFoundError:
        return ret

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
