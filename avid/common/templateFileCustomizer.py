__author__ = 'hentsch'

def writeFileCustomized(templateFilename, targetFilename, replaceDict):
  inputFile = open(templateFilename, 'r')
  content = inputFile.read()
  inputFile.close()

  for key, value in replaceDict.iteritems() :
    content = content.replace(key, str(value))

  outputFile = open(targetFilename, 'w')
  outputFile.write(content)
  outputFile.close()