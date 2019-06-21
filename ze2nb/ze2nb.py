import os
import re
import csv
import json
import html
import nbformat
import codecs
from io import StringIO
import io


MD = re.compile(r'%md\s')
PySpark = re.compile(r'%pyspark\s')
Spark = re.compile(r'%spark\s')
SQL = re.compile(r'%sql\s')
Python = re.compile(r'%python\s')
UNKNOWN_MAGIC = re.compile(r'%\w+\s')
HTML = re.compile(r'%html\s')


def mkdir(path):
    """
    Make a new directory

    :param path: the directory path

    :author: Wenqiang Feng
    :email:  von198@gmail.com
    """
    try:
        os.mkdir(path)
    except OSError:
        pass


def file_load(file_name):
    """
    load zeppelin .json file

    :param file_name: the input .json file name
    :return: encoded text content from .json file

    :author: Wenqiang Feng
    :email:  von198@gmail.com
    """
    return json.load(io.open(file_name, 'r', encoding='utf-8-sig'))


def table_cell_to_html(cell):
    """
    Formats a cell from a Zeppelin TABLE as HTML.

    :param cell: cell from Zeppelin
    :return: zeppelin TABLE as HTML

    :author: Ryan Blue
    :Github:  https://github.com/rdblue
    """
    if HTML.match(cell):
        # the contents is already HTML
        return cell
    else:
        return html.escape(cell)


def table_to_html(tsv):
    """
    Formats the tab-separated content of a Zeppelin TABLE as HTML.

    :param cell: cell from Zeppelin
    :return: zeppelin TABLE as HTML

    :author: Ryan Blue
    :Github:  https://github.com/rdblue
    """
    io = StringIO.StringIO(tsv)
    reader = csv.reader(io, delimiter="\t")
    fields = reader.next()
    column_headers = "".join([ "<th>" + name + "</th>" for name in fields ])
    lines = [
            "<table>",
            "<tr>{column_headers}</tr>".format(column_headers=column_headers)
        ]
    for row in reader:
        lines.append("<tr>" + "".join(["<td>" + table_cell_to_html(cell) + "</td>" for cell in row]) + "</tr>")
    lines.append("</table>")
    return "\n".join(lines)


def convert_parsed(zeppelin_note):
    """
    Converts a Zeppelin note from parsed JSON to a Jupyter Notebook.

    :param zeppelin_note: encoded JSON file
    :return notebook_name: the JSON notebook name
    :return notebook_name: the parsed Jupyter notebook content

    :author: Ryan Blue and Wenqiang Feng
    :github:  https://github.com/rdblue
    :email:  von198@gmail.com
    """
    notebook_name = zeppelin_note['name']

    cells = []
    index = 0
    for paragraph in zeppelin_note['paragraphs']:
        code = paragraph.get('text')
        if not code:
            continue

        code = code.lstrip()

        cell = {}

        if MD.match(code):
            cell['cell_type'] = 'markdown'
            cell['metadata'] = {}
            cell['source'] = code.lstrip('%md').lstrip("\n") # remove '%md'
        elif Python.match(code):
            cell['cell_type'] = 'code'
            cell['execution_count'] = index
            cell['metadata'] = {'autoscroll': 'auto'}
            cell['outputs'] = []
            cell['source'] = code.lstrip('%python').lstrip("\n") # remove '%python'
        elif PySpark.match(code):
            cell['cell_type'] = 'code'
            cell['execution_count'] = index
            cell['metadata'] = {'autoscroll': 'auto'}
            cell['outputs'] = []
            cell['source'] = code.lstrip('%pyspark').lstrip("\n") # remove '%pyspark'
        elif Spark.match(code):
            cell['cell_type'] = 'code'
            cell['execution_count'] = index
            cell['metadata'] = {'autoscroll': 'auto'}
            cell['outputs'] = []
            cell['source'] = code.lstrip('%spark').lstrip("\n") # remove '%spark'            
        elif SQL.match(code) or HTML.match(code):
            cell['cell_type'] = 'code'
            cell['execution_count'] = index
            cell['metadata'] = {}
            cell['outputs'] = []
            cell['source'] = '%' + code # add % to convert to cell magic
        elif UNKNOWN_MAGIC.match(code):
            # use raw cells for unknown magic
            cell['cell_type'] = 'raw'
            cell['metadata'] = {'format': 'text/plain'}
            cell['source'] = code
        else:
            cell['cell_type'] = 'code'
            cell['execution_count'] = index
            cell['metadata'] = {'autoscroll': 'auto'}
            cell['outputs'] = []
            cell['source'] = code

        cells.append(cell)

        result = paragraph.get('result')
        if cell['cell_type'] == 'code' and result:
            if result['code'] == 'SUCCESS':
                result_type = result.get('type')
                output_by_mime_type = {}
                if result_type == 'TEXT':
                    output_by_mime_type['text/plain'] = result['msg']
                elif result_type == 'HTML':
                    output_by_mime_type['text/html'] = result['msg']
                elif result_type == 'TABLE':
                    output_by_mime_type['text/html'] = table_to_html(result['msg'])

                cell['outputs'] = [{
                    'output_type': 'execute_result',
                    'metadata': {},
                    'execution_count': index,
                    'data': output_by_mime_type
                }]

        index += 1

    notebook = nbformat.from_dict({
        "metadata": {
            "kernelspec": {
                "display_name": "Spark 2.0.0",
                "language": "python",
                "name": "spark2"
            },
            "language_info": {
                "codemirror_mode": "text/python",
                "file_extension": ".py",
                "mimetype": "text/python",
                "name": "scala",
                "pygments_lexer": "python",
                "version": "3.6"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2,
        "cells" : cells,
    })
    
    return (notebook_name, notebook)


def write_notebook(notebook_name, notebook, out_path=None):
    """
    Writes parsed JSON notebook to a Jupyter notebook .ipynb file from the notebook name.

    :param notebook_name: JSON notebook name and output Jupyter notebook name
    :param notebook: parsed JSON notebook contents
    :param out_path:  Jupyter notebook output path, the default output path is current directory.

    :author: Wenqiang Feng and Ryan Blue
    :email:  von198@gmail.com
    :github:  https://github.com/rdblue
    """
    """

    If path is None, the output path will be created the notebook name in the current directory.
    """
    if not out_path:
        path = os.getcwd()
    else:
        path = out_path
        mkdir(path)

    filename = path + '/' + notebook_name + '.ipynb'
    print(filename)
    with codecs.open(filename, 'w', encoding='UTF-8') as io:
        nbformat.write(notebook, io)


def ze2nb(file_name, load_path=None, out_path=None, to_nb=True, to_html=True, to_py=True):
    """

    :param file_name: the input JSON file name
    :param load_path: the load path for the input JSON file
    :param out_path: the output path for the converted files
    :param to_nb: the flag for keeping .ipynb
    :param to_html: the flag for converting to .html
    :param to_py: the flag for converting to .py

    :author: Wenqiang Feng and Ryan Blue
    :email:  von198@gmail.com
    :github:  https://github.com/rdblue
    """

    if not load_path:
        load_path = os.getcwd()
    else:
        load_path = load_path

    if not out_path:
        out_path = os.getcwd()
    else:
        out_path = out_path

    file_name = load_path + '/' + file_name

    name, notebook = convert_parsed(file_load(file_name))
    
    # convert to jupyter notebook 
    write_notebook(name, notebook, out_path)
    
    # convert to html
    if to_html:
        os.system('jupyter nbconvert %s' % (out_path+'/'+name + '.ipynb'))
    
    # convert to py
    if to_py:
        os.system("jupyter nbconvert %s --to python" % (out_path+'/'+name + '.ipynb'))

    # remove the .ipynb
    if to_nb==False:
        os.system('rm %s'%(name+'.ipynb'))

