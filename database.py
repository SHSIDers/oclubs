# cond: a tuple, like: "=","user_id",self.uid
# for range: lower bound included, higher bound excluded


def cond_interpret(cond):
    if cond[0] in ['>', '<', '=', '<=', '>=', '<>']:
        if isinstance(cond[2], basestring):
            return cond[1] + cond[0]+"\""+cond[2]+"\""
        else:
            return cond[1] + cond[0]+str(cond[2])
    elif cond[0] == "range":
        return cond[1]+'>='+cond[2][0]+" AND " + cond[1]+'<'+cond[2][1]


def fetch_onerow(table, conds, coldict):
    cols = coldict.keys()
    st = ','.join(cols)
    fconds = []
    for cond in conds:
        fconds.append(cond_interpret(cond))
    fconds = " AND ".join(fconds)
    cur.execute("SELECT %s FROM %s WHERE %s LIMIT 1" % (st, table, fconds))
    ret = {}
    ret.fromkeys(coldict.values())
    read = cur.fetchall()
    if len(read) == 0:
        raise RuntimeError
    i = 0
    for val in read[0]:
        ret[coldict[cols[i]]] = val
        i += 1
    return ret