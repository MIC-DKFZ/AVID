setwd("@WORKING_DIRECTORY@")
csvDataHeader <- read.csv("@CSV_HEADER_FILE@", header=0, sep=";", as.is=TRUE)
csvData <- read.csv("@CSV_DATA_FILE@", header=0, sep=";", as.is=TRUE)

#get max dose value
maxDoseValues <- vector(mode="numeric", length=dim(csvData)[1])
i=1
while (i <= dim(csvData)[1])
{
  maxDoseValues[i] <- csvDataHeader[i,which.min(csvData[i,])]
  i <-i+1
}

png(file="@PNG_FILE@", height=800, width=1200)
par(mar=c(5,5,1,1))
xRange <- range(0,max(maxDoseValues))
yRange <- range(0,1)
plot(xRange, yRange, type = "n", xlab = "Dose (Gy)", ylab = "Volume (%)", cex.axis=2.0, cex.lab=2)
i = 1
while (i <= dim(csvData)[1])
{
	lines(csvDataHeader[i,], csvData[i,], type = "l", col = "blue", lwd=2)
	i <- i+1
}
dev.off()