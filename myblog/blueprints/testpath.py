import os

def print_file_info():
   print(f'__file__={__file__}')
   print(f'os.path.dirname(__file__)={os.path.dirname(__file__)}')
   print(f'os.path.dirname(os.path.dirname(__file__))={os.path.dirname(os.path.dirname(__file__))}')
   basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
   print(f'basedir={basedir}')
   
print_file_info()


import re
from unidecode import unidecode

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def slugify(text, delim=u'-'):
   """Generates an ASCII-only slug."""
   result = []
   for word in _punct_re.split(text.lower()):
      result.extend(unidecode(word).lower().split())
   return str(delim.join(result))  
   

print(slugify(u'My Neighbor Totoro'))
print(slugify(u'邻家的豆豆龙'))
print(slugify(u'となりのトトロ'))