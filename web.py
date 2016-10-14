"""
Used to format showing TSV data in WEB
"""
import sys
import argparse

import flask

from flask import Flask,flash
from flask import request
from flask import render_template

import utils
from errors import *

__author__ = "harvey"

app = Flask(__name__)
parser = argparse.ArgumentParser()
parser.add_argument('--cols', help="table headers seperated by comma")
parser.add_argument('--file', help="tsv data file path")
args = parser.parse_args()

cols, num_records = [], 0
column_num_dict= {}
def pre_check():
    global column_num_dict
    """guarantee the arguments are valid
    """
    global cols, num_records
    print args.file
    if args.file is None:
        parser.print_help()
        sys.exit(1)
    else:
        with open(args.file) as infile:
            head = infile.readline()
            num_records = sum([1 for line in infile])
            if head is not None:
                num_records += 1

        num_cols = len(head.split('\t'))

    if args.cols is None:
        cols = [["colum%d"%i] for i in xrange(num_cols)]
        column_num_dict = dict([(name[0],i) for i, name in enumerate(cols)])
    else:
        cols = [["%s"%col] for col in args.cols.split(',')]
        column_num_dict = dict([(name[0].lower(),i) for i, name in enumerate(cols)])


def load_data():
    with open(args.file) as infile:
        data = [line.strip('\n').split("\t") for line in infile]
    return data

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/data')
def show_data():
    _vals = request.values

    searchContent = _vals['sSearch'] if 'sSearch' in _vals else None
    f = {}

    # deal with the columns header request
    if "columns" in _vals and _vals["columns"] == "true":
        f['columns'] = cols
        return flask.jsonify(**f)

    if 'sSearch' in _vals and _vals['sSearch'].strip(" \t\n") != "":
        try:
            return utils.search(column_num_dict,data_bank,_vals)
        except UnSupportedSearchColumn:
            flash("Make sure the column name exist in table headers.")
        except UnSupportedSearchFormat:
            flash("Please specify the column name for your search E.X.column_name:value")

    start = int(_vals["iDisplayStart"]) if "iDisplayStart" in _vals else 0
    length = int(_vals["iDisplayLength"]) if "iDisplayLength" in _vals else 10
    s_echo = _vals['sEcho'] if 'sEcho' in _vals else "1"
    sort_col = int(_vals['iSortCol_0'])
    sort_asc = True if _vals['sSortDir_0'] == "asc" else False

    data =  sorted(data_bank,
                   key = lambda x:utils.safe_int(x[sort_col]),
                   reverse = not sort_asc
                   )
    f.update({
            "sEcho": s_echo,
            "iTotalRecords": num_records,
            "iTotalDisplayRecords": num_records,
        })

    f['aaData'] = data[start : start+length]
    return flask.jsonify(**f)

if __name__ == "__main__":
    pre_check()
    data_bank = load_data()
    # set as part of the config
    SECRET_KEY = 'many random bytes'
    # or set directly on the app
    app.secret_key = 'many random bytes'

    app.run(host='0.0.0.0', port=9001)
