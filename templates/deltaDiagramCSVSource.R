setwd("@WORKING_DIRECTORY@")
csvData <- read.csv("@CSV_FILE@", header=0, sep=";", as.is=TRUE)
png(file="@PNG_FILE@", height=700, width=1200)
par(mar=c(5,5,1,1))

i = 3
deltaData <- csvData
deltaData[2,]=0
while (i <= dim(csvData)[1])
{
  deltaData[i,]=csvData[i,]-csvData[2,]
  i <- i+1
}

xRange <- range(0,max(deltaData[1,]))
yRange <- range(min(deltaData[2:dim(deltaData)[1],]),max(deltaData[2:dim(deltaData)[1],]))
plot(xRange, yRange, type = "n", xlab = "Fractions", ylab = expression(paste("", Delta, "Dose (Gy)")), cex.axis=2.0, cex.lab=2)
grid (NA,NULL) 
i = 3
while (i <= dim(deltaData)[1])
{
	lines(deltaData[1,], deltaData[i,], type = "l", col = "blue", lwd=2)
	i <- i+1
}
lines(deltaData[1,], deltaData[2,], type = "l", col = "black", lwd=3)
dev.off()