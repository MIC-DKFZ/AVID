def mean(list):
  return sum(list)/list.__len__()

def variance(list):
  meanValue = mean(list)
  temp = 0

  for i in range(list.__len__()):
      temp += (list[i] - meanValue) * (list[i] - meanValue)
  return temp / list.__len__()