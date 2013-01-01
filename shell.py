#!/usr/bin/python

import IPython, os

app_id = "application"
os.environ['APPLICATION_ID'] = app_id
datastore_file = '/dev/null'
from google.appengine.api import apiproxy_stub_map,datastore_file_stub
apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap() 
stub = datastore_file_stub.DatastoreFileStub(app_id, datastore_file, '/')
apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', stub)

IPython.embed()
