#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import unicode_literals

from flask import g
import MySQLdb

from oclubs.exceptions import NoRow

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
        return ' '.join([var, op, _encode(const)])
    elif op.lower() in ["and", "or"]:
        return (' %s ' % op.upper()).join(
            [__parse_cond(one_cond) for one_cond in conds])
    elif op.lower() == "range":
        # (lo, hi]
        var, (lo, hi) = conds
        return __parse_cond('and', ('>=', var, lo), ('<', var, hi))


def _parse_comp_cond(cond, forcelimit=None):
    conddict = {
        'join': [],  # list of tuple (type, table, [(var1, var2), ...])
        'where': [],  # list of tuple (type, var, const)
        'group': [],  # list of vars
        'having': [],  # same as where
        'order': [],  # tuple (var, is_asc)
        'limit': None  # None or num or (lo, hi)
    }
    if isinstance(cond, list):
        # this is a simple cond
        conddict['where'] = cond
    else:
        conddict.update(cond)

    if forcelimit:
        conddict['limit'] = forcelimit

    sql = []

    for jointype, table, conds in conddict['JOIN']:
        sql.append(jointype.upper + ' JOIN ' + table)
        sql.append('ON ' + ' AND '.join(
            [var1 + ' = ' + var2 for var1, var2 in conds]
        ))

    if conddict['where']:
        sql.append('WHERE ' + _parse_cond(conddict['where']))

    if conddict['group']:
        sql.append('GROUP BY ' + ','.join(conddict['group']))

    if conddict['having']:
        sql.append('HAVING ' + _parse_cond(conddict['having']))

    if conddict['order']:
        sql.append('ORDER BY ' + ','.join([
            var + ' ' + ('ASC' if is_asc else 'DESC')
            for var, is_asc in conddict['order']
        ]))

    if conddict['limit']:
        sql.append('LIMIT ' + (
            '%d,%d' % conddict['limit']
            if isinstance(conddict['limit'], tuple) else
            str(conddict['limit'])
        ))

    return ' '.join(sql)


def _encode(obj):
    if obj is None:
        return 'NULL'
    elif isinstance(obj, (bool, int, long, float)):
        return str(obj)
    elif isinstance(obj, basestring):
        return '"%s"' % MySQLdb.escape_string(obj)
    else:
        import json
        return _encode(json.dumps(obj))


def _mk_multi_return(row, cols, coldict):
    ret = {}
    i = 0
    for val in row:
        ret[coldict[cols[i]]] = val
        i += 1
    return ret


def _execute(sql, iswrite=False):
    """
    Internal sql execution handling for each request.

    MySQLdb is not thread-safe.
    """
    db = g.get('dbconnection', None)
    if not db:
        db = MySQLdb.connect(
            host="localhost",
            user="root",
            db="oclubs",
            charset='utf8',
            use_unicode=True
        )
        g.dbconnection = db
    cur = db.cursor()

    try:
        if iswrite and not g.get('dbtransaction', False):
            cur.execute("START TRANSACTION;")
            g.dbtransaction = True

        cur.execute(sql)

        return cur.fetchall()
    finally:
        cur.close()


# TODO
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
            g.dbtransaction = False


def fetch_onerow(table, conds, coldict):
    cols = coldict.keys()
    st = ','.join(cols)
    conds = _parse_comp_cond(conds, forcelimit=1)

    rows = _execute("SELECT %s FROM %s %s;"
                    % (st, table, conds))
    if not rows:
        raise NoRow

    return _mk_multi_return(rows[0], cols, coldict)


def fetch_oneentry(table, conds, col):
    conds = _parse_comp_cond(conds, forcelimit=1)

    rows = _execute("SELECT %s FROM %s %s;"
                    % (col, table, conds))
    if not rows:
        raise NoRow

    return rows[0][0]


def fetch_onecol(table, conds, col):
    conds = _parse_comp_cond(conds)

    rows = _execute("SELECT %s FROM %s %s;"
                    % (col, table, conds))

    return [val for val, in rows]


def fetch_multirow(table, conds, coldict):
    cols = coldict.keys()
    st = ','.join(cols)
    conds = _parse_comp_cond(conds)

    rows = _execute("SELECT %s FROM %s %s;" % (st, table, conds))

    return [_mk_multi_return(row, cols, coldict) for row in rows]


def update_row(table, conds, update):
    conds = _parse_comp_cond(conds)
    setto = ["%s=%s" % (key, _encode(val)) for key, val in update.items()]
    setto = ','.join(setto)

    return _execute('UPDATE %s SET %s %s;' % (table, setto, conds),
                    write=True)


def insert_onerow(table, row):
    keys = ','.join(row.keys())
    values = ','.join([_encode(value) for value in row.values()])

    return _execute("INSERT INTO %s (%s) VALUES (%s);" % (table, keys, values),
                    write=True)
