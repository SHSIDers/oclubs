#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#

from __future__ import unicode_literals

from flask import g
import MySQLdb


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

    if iswrite and not g.get('dbtransaction', False):
        cur.execute("START TRANSACTION;")
        g.dbtransaction = True

    cur.execute(sql)

    return cur.fetchall()


# FIXME
def finish_transaction(commit=True):
    """Exported function for flask."""
    if g.get('dbconnection', None) and g.get('dbtransaction', False):
        g.dbconnection.cursor().execute('COMMIT;' if commit else 'ROLLBACK;')
        g.dbtransaction = False


def fetch_onerow(table, conds, coldict):
    cols = coldict.keys()
    st = ','.join(cols)
    conds = _parse_cond(conds)

    rows = _execute("SELECT %s FROM %s WHERE %s LIMIT 1;"
                    % (st, table, conds))
    if not rows:
        raise RuntimeError

    return _mk_multi_return(rows[0], cols, coldict)


def fetch_oneentry(table, conds, col):
    conds = _parse_cond(conds)

    rows = _execute("SELECT %s FROM %s WHERE %s LIMIT 1;"
                    % (col, table, conds))
    if not rows:
        raise RuntimeError

    return rows[0][0]


def fetch_onecol(table, conds, col):
    conds = _parse_cond(conds)

    rows = _execute("SELECT %s FROM %s WHERE %s;"
                    % (col, table, conds))

    return [val for val, in rows]


def fetch_multirow(table, conds, coldict):
    cols = coldict.keys()
    st = ','.join(cols)
    conds = _parse_cond(conds)

    rows = _execute("SELECT %s FROM %s WHERE %s;" % (st, table, conds))

    return [_mk_multi_return(row, cols, coldict) for row in rows]


def insert_onerow(table, row):
    keys = ','.join(row.keys())
    values = ','.join([_encode(value) for value in row.values()])

    return _execute("INSERT INTO %s (%s) VALUES (%s);" % (table, keys, values),
                    write=True)


def update_allrow(table, conds, update):
    conds = _parse_cond(conds)
    setto = ["%s=%s" % (key, _encode(val)) for key, val in update.items()]
    setto = ','.join(setto)

    return _execute('UPDATE %s SET %s WHERE %s;' % (table, setto, conds),
                    write=True)
