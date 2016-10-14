require("forecast")
csvFile <- "@CSV_FILE@"
data <- read.csv(csvFile, header=FALSE, sep=";", as.is=TRUE)
dataMatrix <- as.matrix(data)
dataMatrix2 <- matrix(dataMatrix, ncol = ncol(dataMatrix), dimnames = NULL)
dataMatrix2 <- dataMatrix[-1,]
dataMatrix2[1]=0
dataMatrix2 <- unname(dataMatrix2)
dataMatrix2 <- as.numeric(dataMatrix2)
timeSeries <- ts(dataMatrix2)

startTime <- 3
endTime <- @ENDTIME@+3
sampling <- 1
lastFractionDose <- matrix(0,endTime,5)
for (i in seq(startTime, endTime-1, sampling)){
  fit <- forecast::auto.arima(timeSeries[startTime:i-1])
  fc <- forecast::forecast(fit, h=endTime-i)
  
  lastFractionDose[i,1]<-i-3
  mean <- fc$mean[length(fc$mean)]
  lower <- fc$lower[length(fc$lower)]
  upper <- fc$upper[length(fc$upper)]
  
  #lower 95% quantil
  lastFractionDose[i,2] = lower
  #50% quantil (mean)
  lastFractionDose[i,3] = mean
  #upper 95% quantil
  lastFractionDose[i,4] = upper
  #arima parametrization
  lastFractionDose[i,5] = fc$method
}
lastFractionDose[endTime,1]<-endTime-3
lastFractionDose[endTime,2] = timeSeries[endTime-1]
lastFractionDose[endTime,3] = timeSeries[endTime-1]
lastFractionDose[endTime,4] = timeSeries[endTime-1]
lastFractionDose[endTime,5] = "actual value"

lastFractionDose[1,1] = "@ROW_KEY@/@COLUMN_KEY@"
lastFractionDose[1,2] = 0.05
lastFractionDose[1,3] = 0.5
lastFractionDose[1,4] = 0.95
lastFractionDose[1,5] = "Prediction Method"

resultCsvFile <- "@RESULT_CSV_FILE@"

write.table(lastFractionDose, file=resultCsvFile, col.names=FALSE, row.names=FALSE, sep=";")