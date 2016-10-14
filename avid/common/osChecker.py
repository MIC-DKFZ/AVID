import os
import errno
import exceptions

def checkAndCreateDir(completePath):
  """ generates a directory """
  try:
    os.makedirs(completePath)
  except exceptions.OSError as exc:
    if exc.errno != errno.EEXIST:
	  raise exc
    pass