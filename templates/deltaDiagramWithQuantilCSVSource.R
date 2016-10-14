setwd("@WORKING_DIRECTORY@")
csvData <- read.csv("@CSVDATA_FILE@", header=0, sep=";", as.is=TRUE)
csvBaseline <- read.csv("@CSVBASELINE_FILE@", header=0, sep=";", as.is=TRUE)
png(file="@PNG_FILE@", height=700, width=1200)
par(mar=c(5,5,1,1))

i <- 2
deltaData <- csvData
deltaData[2,]=0
while (i <= dim(csvData)[1])
{
  deltaData[i+1,]=csvData[i,]-csvBaseline[2,]
  i <- i+1
}

xRange <- range(0,max(deltaData[1,]))
yRange <- range(min(deltaData[2:dim(deltaData)[1],]),max(deltaData[2:dim(deltaData)[1],]))
plot(xRange, yRange, type = "n", xlab = "Fractions", ylab = expression(paste("", Delta, "Dose (Gy)")), cex.axis=2.0, cex.lab=2)
grid (NA,NULL) 

#Compute quantils
qmin <- rep(0,dim(deltaData)[2])
q1 <- rep(0,dim(deltaData)[2])
q2 <- rep(0,dim(deltaData)[2])
q3 <- rep(0,dim(deltaData)[2])
qmax <- rep(0,dim(deltaData)[2])
i <- 1
while (i <= dim(deltaData)[2])
{
  qs <- quantile(deltaData[3:dim(deltaData)[1],i])
  qmin[i] <- qs[1]
  q1[i] <- qs[2]
  q2[i] <- qs[3]
  q3[i] <- qs[4]
  qmax[i] <- qs[5]
  i <- i+1
}

i <- 3
while (i <= dim(deltaData)[1])
{
	lines(deltaData[1,], deltaData[i,], type = "l", col = "gray", lwd=1)
	i <- i+1
}
lines(deltaData[1,], deltaData[2,], type = "l", col = "orange", lwd=4)
lines(deltaData[1,], qmin, type = "l", col = "indian red", lwd=3)
lines(deltaData[1,], qmax, type = "l", col = "indian red", lwd=3)
lines(deltaData[1,], q1, type = "l", col = "red", lwd=3)
lines(deltaData[1,], q2, type = "l", col = "dark red", lwd=3)
lines(deltaData[1,], q3, type = "l", col = "red", lwd=3)

legend("topleft", c("planned","variation","min, max","Q1, Q3", "median"), lty=c(1,1,1,1,1), lwd=c(3,3,3,3,3),col=c("orange","gray","indian red","red","dark red"), cex = 2.5)
dev.off()