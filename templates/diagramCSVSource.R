setwd("@WORKING_DIRECTORY@")
csvData <- read.csv("@CSVDATA_FILE@", header=0, sep=";", as.is=TRUE)
csvBaseline <- read.csv("@CSVBASELINE_FILE@", header=0, sep=";", as.is=TRUE)
png(file="@PNG_FILE@", height=700, width=1200)
par(mar=c(5,5,3,1))
xRange <- range(0,max(csvData[1,dim(csvData)[2]]))
yRange <- range(0,max(csvData[2:dim(csvData)[1],dim(csvData)[2]]))
plot(xRange, yRange, type = "n", xlab = "@XAXIS_NAME@", ylab = "@YAXIS_NAME@", cex.axis=2.0, cex.lab=2.0)
title(main="@TITLE_NAME@", cex.main=2)
grid (NA,NULL) 
i = 2
while (i <= dim(csvData)[1])
{
	lines(csvData[1,2:dim(csvData)[2]], csvData[i,2:dim(csvData)[2]], type = "l", col = "red", lwd=2)
	i <- i+1
}
lines(csvBaseline[1,2:dim(csvData)[2]], csvBaseline[2,2:dim(csvData)[2]], type = "l", col = "orange", lwd=3)
dev.off()