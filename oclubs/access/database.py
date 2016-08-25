#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import absolute_import

from flask import g
import MySQLdb
import MySQLdb.constants.CLIENT

from oclubs.access import get_secret
from oclubs.exceptions import NoRow, AlreadyExists


class RawSQL(object):
    """Class to signal a raw SQL part of a query. - DANGEROUS!"""
    def __init__(self, sql):
        self._sql = _strify(sql)

    @property
    def sql(self):
        return self._sql


def _parse_cond(conds):
    return ' AND '.join([__parse_cond(one_cond) for one_cond in conds])


def __parse_cond(cond):
    return '(%s)' % ___parse_cond(cond)


def ___parse_cond(cond):
    op, conds = cond[0], cond[1:]
    if op in ['>', '<', '=', '<=', '>=', '!=']:
        var, const = conds
        if const is None:
            op = {'=': 'IS', '!=': 'IS NOT'}.get(op, op)
        return ' '.join([_encode_name(var), _strify(op), _encode(const)])
    elif op.lower() in ['and', 'or']:
        return (' %s ' % op.upper()).join(
            [__parse_cond(one_cond) for one_cond in conds])
    elif op.lower() == 'range':
        # [lo, hi)
        var, (lo, hi) = conds
        return __parse_cond('and', ('>=', var, lo), ('<', var, hi))
    elif op.lower() == 'in':
        var, const = conds
        const = ','.join([_encode(elemt) for elemt in const])
        return '%s IN (%s)' % (_encode_name(var), const)


def expand_cond(cond):
    conddict = {
        'join': [],  # list of tuple (type, table, [(var1, var2), ...])
        'where': [],  # list of tuple (type, var, const)
        'group': [],  # list of vars
        'having': [],  # same as where
        'order': [],  # tuple (var, is_asc)
        'limit': None  # None or count or (offset, count)
    }
    if isinstance(cond, list):
        # this is a simple cond
        conddict['where'] = cond
    elif 'where' in cond:
        conddict.update(cond)
    else:
        conddict['where'] = [('=', key, value) for key, value in cond.items()]

    return conddict


def _parse_comp_cond(cond, forcelimit=None):
    conddict = expand_cond(cond)

    if forcelimit:
        conddict['limit'] = forcelimit

    sql = []

    for jointype, table, conds in conddict['join']:
        sql.append(_strify(jointype.upper()) + ' JOIN ' + _encode_name(table))
        sql.append('ON ' + ' AND '.join([
            _encode_name(var1) + ' = ' + _encode_name(var2)
            for var1, var2 in conds
        ]))

    if conddict['where']:
        sql.append('WHERE ' + _parse_cond(conddict['where']))

    if conddict['group']:
        sql.append('GROUP BY ' + ','.join(_encode_name(conddict['group'])))

    if conddict['having']:
        sql.append('HAVING ' + _parse_cond(conddict['having']))

    if conddict['order']:
        sql.append('ORDER BY ' + ','.join([
            _encode_name(var) + ' ' + ('ASC' if is_asc else 'DESC')
            for var, is_asc in conddict['order']
        ]))

    if conddict['limit']:
        sql.append('LIMIT ' + (
            '%s,%s' % tuple(map(_encode, conddict['limit']))
            if isinstance(conddict['limit'], tuple) else
            _encode(conddict['limit'])
        ))

    return ' '.join(sql)


def _strify(st):
    if isinstance(st, unicode):
        return st.encode('utf-8')
    return st


def _encode(obj):
    if obj is None:
        return 'NULL'
    elif isinstance(obj, (bool, int, long, float)):
        return str(obj)
    elif isinstance(obj, basestring):
        # SECURITY NOTE: PAY SPECIAL CARE THIS WHEN CONNECTION IS NOT utf-8
        # CHECK THE SAFETY OF THE ENCODING:
        #
        # encoding = 'utf-8'
        # p = ['\\', '"', "'"]
        # for i in range(0x110000):
        #     c = unichr(i)
        #     try:
        #         e = c.encode(encoding)
        #     except UnicodeEncodeError:
        #         pass
        #     else:
        #         if any(map(lambda q: q in e, p)) and c not in p:
        #             print i, c
        #
        # DO NOT USE THIS IF ANYTHING IS IN THE OUTPUT

        return "'%s'" % MySQLdb.escape_string(_strify(obj))
    else:
        import json
        return _encode(json.dumps(obj))


def _encode_name(identifier):
    if isinstance(identifier, RawSQL):
        return identifier.sql
    elif isinstance(identifier, list):
        return ','.join([_encode_name(item) for item in identifier])
    return '`%s`' % MySQLdb.escape_string(_strify(identifier))


def _parse_extras(kwargs):
    extradict = {
        'distinct': 'DISTINCT',
        '_calc_found': 'SQL_CALC_FOUND_ROWS'
    }

    return ' '.join([val for key, val in extradict.items()
                     if key in kwargs and kwargs[key]])


def _mk_multi_return(row, cols, coldict):
    ret = {}
    i = 0
    for val in row:
        ret[coldict[cols[i]]] = val
        i += 1
    return ret


def _execute(sql, write=False, ret='fetch'):
    """
    Internal sql execution handling for each request.

    MySQLdb is not thread-safe.
    """
    db = g.get('dbconnection', None)
    if not db:
        db = MySQLdb.connect(
            host='localhost',
            user='root',
            passwd=get_secret('mariadb_pw'),
            db='oclubs',
            charset='utf8',
            use_unicode=True,
        )
        g.dbconnection = db
    cur = db.cursor()

    try:
        if write and not g.get('dbtransaction', False):
            cur.execute("START TRANSACTION;")
            g.dbtransaction = True

        cur.execute(sql)

        if ret == 'fetch':
            return cur.fetchall()
        elif ret == 'rowcount':
            return cur.rowcount
        elif ret == 'lastrowid':
            return cur.lastrowid
        else:  # fetch
            return cur.fetchall()
    finally:
        cur.close()


def done(commit=True):
    """Exported function for flask."""
    if g.get('dbconnection', None):
        try:
            if g.get('dbtransaction', False):
                if commit:
                    g.dbconnection.commit()
                else:
                    g.dbconnection.rollback()
        finally:
            g.dbconnection.close()
            g.dbconnection = False
            g.dbtransaction = False


def fetch_info(info):
    return _execute("SELECT %s;" % _encode_name(info))[0][0]


def fetch_onerow(table, coldict, conds, **kwargs):
    cols = coldict.keys()
    st = _encode_name(cols)
    conds = _parse_comp_cond(conds, forcelimit=1)

    rows = _execute("SELECT %s %s FROM %s %s;"
                    % (_parse_extras(kwargs), st, _encode_name(table), conds))
    if not rows:
        raise NoRow

    return _mk_multi_return(rows[0], cols, coldict)


def fetch_oneentry(table, col, conds, **kwargs):
    conds = _parse_comp_cond(conds, forcelimit=1)

    rows = _execute("SELECT %s %s FROM %s %s;"
                    % (_parse_extras(kwargs), _encode_name(col),
                       _encode_name(table), conds))
    if not rows:
        raise NoRow

    return rows[0][0]


def fetch_onecol(table, col, conds, **kwargs):
    conds = _parse_comp_cond(conds)

    rows = _execute("SELECT %s %s FROM %s %s;"
                    % (_parse_extras(kwargs), _encode_name(col),
                       _encode_name(table), conds))

    return [val for val, in rows]


def fetch_multirow(table, coldict, conds, **kwargs):
    cols = coldict.keys()
    st = _encode_name(cols)
    conds = _parse_comp_cond(conds)

    rows = _execute("SELECT %s %s FROM %s %s;"
                    % (_parse_extras(kwargs), st, _encode_name(table), conds))

    return [_mk_multi_return(row, cols, coldict) for row in rows]


def insert_row(table, insert):
    try:
        keys = _encode_name(insert.keys())
        values = ','.join([_encode(value) for value in insert.values()])

        return _execute("INSERT INTO %s (%s) VALUES (%s);"
                        % (_encode_name(table), keys, values),
                        write=True, ret='lastrowid')
    except MySQLdb.IntegrityError as e:
        if e[0] == 1062:
            raise AlreadyExists
        raise


def insert_or_update_row(table, insert, update):
    if update:
        keys = _encode_name(insert.keys())
        values = ','.join([_encode(value) for value in insert.values()])

        update = ["%s=%s" % (_encode_name(key), _encode(val))
                  for key, val in update.items()]
        update = ','.join(update)

        return _execute(
            "INSERT INTO %s (%s) VALUES (%s) ON DUPLICATE KEY UPDATE %s;"
            % (_encode_name(table), keys, values, update),
            write=True, ret='lastrowid')
    else:
        try:
            return insert_row(table, insert)
        except AlreadyExists:
            return 0


def update_row(table, update, conds):
    conds = _parse_comp_cond(conds)
    update = ["%s=%s" % (_encode_name(key), _encode(val))
              for key, val in update.items()]
    update = ','.join(update)

    rows = _execute('UPDATE %s SET %s %s;'
                    % (_encode_name(table), update, conds),
                    write=True, ret='rowcount')

    if not rows:
        raise NoRow

    return rows


def delete_rows(table, conds):
    conds = _parse_comp_cond(conds)

    rows = _execute("DELETE FROM %s %s;" % (_encode_name(table), conds),
                    write=True, ret='rowcount')

    if not rows:
        raise NoRow

    return rows
