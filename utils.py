# TODO need to deal with the multi-task situdation.

import flask
import sys

from flask import flash
from collections import OrderedDict

from errors import *

CACHE_SIZE = 20;
cache = OrderedDict()

def safe_int(x):
    try:
        return int(x)
    except:
        pass
    return x

def search(column_num_dict,data_bank,_vals):
    global last_content,last_filtered_data
    f = {}
    start = int(_vals["iDisplayStart"]) if "iDisplayStart" in _vals else 0
    length = int(_vals["iDisplayLength"]) if "iDisplayLength" in _vals else 10
    s_echo = _vals['sEcho'] if 'sEcho' in _vals else "1"
    sort_col = int(_vals['iSortCol_0'])
    sort_asc = True if _vals['sSortDir_0'] == "asc" else False
    content = _vals['sSearch'].lower().strip("\t\n ")

    
    # reuse previous results
    if content in cache: 
        data = cache[content]
        f.update({
                "sEcho": s_echo,
                "iTotalRecords": len(data_bank),
                "iTotalDisplayRecords": len(data),
            })
        data =  sorted(data,key = lambda x:safe_int(x[sort_col]), reverse = not sort_asc)
        f['aaData'] = data[start:start+length]
        return  flask.jsonify(**f);

    conts = content.split(":")

    if len(conts) < 2:
        raise UnSupportedSearchFormat("Unsupported search format.")

    column, value = conts[0].lower(), conts[1]
    index_column = column_num_dict.get(column,None)
    print >> sys.stderr, "=" * 20
    print >> sys.stderr, conts,index_column,column_num_dict
    print >> sys.stderr, "=" * 20

    if index_column is None:
        raise UnSupportedSearchColumn("column[%s] did not exist in columns dict"%column)

    filtered_data = filter(lambda x:value in x[index_column].lower(),data_bank)
    
    # check cache and insert the new record
    if len(cache) > CACHE_SIZE:
        cache.popitem()
    cache[content] = filtered_data

    f.update({
            "sEcho": s_echo,
            "iTotalRecords": len(data_bank),
            "iTotalDisplayRecords": len(filtered_data),
        })

    data =  sorted(filtered_data,key = lambda x:safe_int(x[sort_col]), reverse = not sort_asc)
    f['aaData'] = data[start:start+length]
    return flask.jsonify(**f)
