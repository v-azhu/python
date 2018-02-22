
#setup.py
from distutils.core import setup
import os,py2exe
from glob import glob
import version
from platform import platform

project='pymonitor'
cmdList=['monitor.py','encryption.py']
exeList=[i.replace('.py','.exe') for i in cmdList]
scripts=[{'script':i} for i in cmdList]
includes=['lxml.etree','lxml._elementpath','cx_Oracle','gzip']
all_excludes=['oci.dll','oraociei11.dll']
packages=['oracle']
pydata_files=[('config',['config/mconfig.xml','config/readme.txt'])]
setup(
      name=project,
      version=version.version,
      author="ZhuYunSheng",
      authorEmain="awen.zhu@hotmail.com;awen.zhu@hotmail.com",
      description="simple monitor tool for py system.",
      url="",
      platform=['windows'],
      packages=packages,
      console=scripts,
      data_files=pydata_files,
      option={"py2exe":{
                        "compressed":2,
                        "optimize":2,
                        "includes":includes,
                        "all_excludes":all_excludes,
                        "dist_dir":"dist",
                        "xref":False,
                        "skip_archive":False,
                        "ascii":False,
                        "custom_boot_script":''}
             }
      )
