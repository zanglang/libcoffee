# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os

from google.appengine.api import memcache
from keycache import serialize_models, deserialize_models
  

ACTIVE_ON_DEV_SERVER = False
      
def memoize(time=1000000, force_cache=False):
    
    """Decorator to memoize functions using memcache.
    
    Optional Args:
      time - duration before cache is refreshed
      force_cache - forces caching on dev_server (useful for APIs, etc.)
      force_run - forces fxn to run and cache to refresh
    
    Usage:
      
      @memoize(86400)
      def updateAllEntities(key_name, params, force_run=False):
         entity = Model.get_by_key_name(key_name)
         for param in params.items():
            setattr(entity, param.key(), param.value())
            db.put(entity) 
      
    
    """
    def decorator(fxn):
        def wrapper(*args, **kwargs):
            approved_args=['Link', 'Key', 'str', 'unicode', 'int','float', 'bool'] 
            arg_string = ""
            for arg in args:
              if type(arg).__name__ in approved_args: 
                arg_string += str( arg )
              else: raise UnsupportedArgumentError(arg)
            for kwarg in kwargs.items():
              if type(kwarg[1]).__name__ in approved_args: 
                arg_string += str( kwarg[1] )
              else: raise UnsupportedArgumentError(arg)             
            key = fxn.__name__ + arg_string
            logging.debug('caching key: %s' % key)
            data = deserialize_models(memcache.get(key))
            if Debug():
                if not ACTIVE_ON_DEV_SERVER and not force_cache: 
                  return fxn(*args, **kwargs) 
            if kwargs.get('force_run'):
               logging.info("forced execution of %s" % fxn.__name__)
            elif data:
                if data.__class__ == NoneVal: 
                   data = None
                return data
            data = fxn(*args, **kwargs)
            if data is None: data = NoneVal() 
            memcache.set(key, serialize_models(data), time)
            return data
        return wrapper
    return decorator  



""" Util Methods """

class UnsupportedArgumentError(Exception):
  ''' An unsupported argument has been passed to Memoize fxn '''
  def __init__(self, value):
       self.arg = value
  def __str__(self):
       return repr(type(self.arg).__name__ + " is not a supported arg type")

def Debug():
    '''return True if script is running in the development envionment'''
    return  'Development' in os.environ['SERVER_SOFTWARE']
    
    
""" Singleton Classes """
    
class NoneVal():
  ''' A replacement for None, so a memoized fxn can return a None val
  without making the Memoize fxn assume that the "None" means there
  isn't a cached value '''
  pass
