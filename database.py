import MySQLdb
db = MySQLdb.connect(host="localhost", user="root", db="oclubs")
cur = db.cursor()

# cond: a tuple, like: "=","user_id",self.uid
# for range: lower bound included, higher bound excluded


def cond_interpret(cond):
    if cond[0] in ['>', '<', '=', '<=', '>=', '<>']:
        if isinstance(cond[2], basestring):
            return cond[1] + cond[0]+"\""+cond[2]+"\""
        else:
            return cond[1] + cond[0]+str(cond[2])
    elif cond[0] == "range":
        assert (isinstance(cond[2][0], int) or isinstance(cond[2][0], float))
        assert (isinstance(cond[2][1], int) or isinstance(cond[2][1], float))
        return cond[1]+'>='+cond[2][0]+" AND " + cond[1]+'<'+cond[2][1]


def fetch_onerow(table, conds, coldict, isand=True):
    cols = coldict.keys()
    st = ','.join(cols)
    fconds = []
    for cond in conds:
        fconds.append(cond_interpret(cond))
    if isand:
        fconds = " AND ".join(fconds)
    else:
        fconds = " OR ".join(fconds)
    cur.execute("SELECT %s FROM %s WHERE %s LIMIT 1" % (st, table, fconds))
    read = cur.fetchall()
    if len(read) == 0:
        raise RuntimeError
    ret = {}
    ret.fromkeys(coldict.values())
    i = 0
    for val in read[0]:
        ret[coldict[cols[i]]] = val
        i += 1
    return ret


def fetch_oneblock(table, conds, col, isand=True):
    fconds = []
    for cond in conds:
        fconds.append(cond_interpret(cond))
    if isand:
        fconds = " AND ".join(fconds)
    else:
        fconds = " OR ".join(fconds)
    cur.execute("SELECT %s FROM %s WHERE %s LIMIT 1" % (col, table, fconds))
    read = cur.fetchall()
    if len(read) == 0:
        raise RuntimeError
    return read[0][0]


def fetch_allrow(table, conds, coldict, isand=True):
    cols = coldict.keys()
    st = ','.join(cols)
    fconds = []
    for cond in conds:
        fconds.append(cond_interpret(cond))
    if isand:
        fconds = " AND ".join(fconds)
    else:
        fconds = " OR ".join(fconds)
    cur.execute("SELECT %s FROM %s WHERE %s" % (st, table, fconds))
    reads = cur.fetchall()
    if len(reads) == 0:
        raise RuntimeError
    rows = []
    for read in reads:
        row = {}
        row.fromkeys(coldict.values)
        i = 0
        for val in read:
            row[coldict[cols[i]]] = val
            i += 1
        rows.append(row)
    return rows


# dictrow: a dictionary, containing info about the new row
def insert_onerow(table, dictrow):
    keys = ','.join(dictrow.keys())
    values = []
    for value in dictrow.values():
        if isinstance(value, basestring):
            values.append("\"%s\"" % (value))
        else:
            values.append(value)
    strval = ','.join(values)
    cur.execute("START TRANSACTION")
    cur.execute("INSERT INTO %s (%s) VALUES (%s)" % (table, keys, strval))
    cur.execute("COMMIT")
    return cur.fetchall()


# dictup: a dictionary, containing info about which row should be updated
def update_allrow(table, conds, dictupdate, isand=True):
    fconds = []
    for cond in conds:
        fconds.append(cond_interpret(cond))
    if isand:
        fconds = " AND ".join(fconds)
    else:
        fconds = " OR ".join(fconds)
    items = dictupdate.items()
    setto = []
    for item in items:
        setto.append("%s=%s" % (item[0], item[1]))
    setto = ', '.join(setto)
    cur.execute("START TRANSACTION")
    cur.execute('UPDATE %s SET %s WHERE %s' % (table, setto, fconds))
    cur.execute("COMMIT")
    return cur.fetchall()
