from setuptools import setup

setup(name                =  'py-tpg'                                      ,
      version             =  '0.1.0'                                       ,
      description         =  'Client for TPG API.'                         ,
      url                 =  'http://github.com/artemis-beta/py-tpg'       ,
      author              =  'Kristian Zarebski'                           ,
      author_email        =  'krizar312@yahoo.co.uk'                       ,
      license             =  'MIT'                                         ,
      packages            =  ['py-tpg', 'tabulate']                        ,
      zip_safe            =  False                                         ,
      tests_require       =  ['nose2']                                    
     )
