from flask import Flask, escape, request,render_template,render_template_string
from json2html import *
import json
import os

#Check workspace
cwd = os.getcwd()
if cwd.split('/')[-1]!='snmp' : os.chdir("Scripts/python/snmp/")
app = Flask(__name__)

#Main interface
@app.route('/test') 
def test():
    return render_template('index.html')

#Paths viewer interface
@app.route('/paths_view')
def paths_view():
    #Load files
    f=open("json/paths.json",)
    paths=json.load(f)
    f.close()
    paths_html=''
    i=1
    #Dynamic HTML tables creation
    for path in paths['paths']:
        length=str(len(path['nodes']))
        paths_html=paths_html+'<div class="card"><div class="card-header"><h3>Path '+str(i)+'</h3> Length : '+length+' nodes</div><div class="card-body">'
        converted_json=json2html.convert(path,table_attributes="id=\"info-table"+str(i)+"\" class=\"table table-bordered table-hover\"")
        paths_html=paths_html+converted_json
        paths_html=paths_html+'</div></div><br>'
        i=i+1
    return render_template('paths_viewer.html',paths_html=paths_html)

# app.run('0.0.0.0',port=12345,debug=True)
app.run('0.0.0.0',port=5555,debug=True)
