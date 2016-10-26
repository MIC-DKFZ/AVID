from math import sqrt

def mean(list):
  try:
    return sum(list)/len(list)
  except:
    return None

def variance(list):
  meanValue = mean(list)
  temp = 0

  try:
    for i in range(len(list)):
        temp += (list[i] - meanValue) * (list[i] - meanValue)
    return temp / len(list)
  except:
    return None
  
def sd(list):
  var = variance(list)
  
  try:
    return sqrt(var)
  except:
    return None