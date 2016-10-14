setwd("@WORKING_DIRECTORY@")
csvData <- read.csv("@CSVDATA_FILE@", header=0, sep=";", as.is=TRUE)
csvBaseline <- read.csv("@CSVBASELINE_FILE@", header=0, sep=";", as.is=TRUE)
csvAdditionalData <- read.csv("@CSVADDITIONALDATA_FILE@", header=0, sep=";", as.is=TRUE)
png(file="@PNG_FILE@", height=500, width=500)

csvDataLastFraction = as.numeric(csvData[,dim(csvData)[2]])
csvBaselineLastFraction = as.numeric(csvBaseline[,dim(csvBaseline)[2]])
csvAdditionalDataLastFraction = as.numeric(csvAdditionalData[,dim(csvAdditionalData)[2]])

limits = c(min(csvDataLastFraction[2:length(csvDataLastFraction)],csvBaselineLastFraction[2:length(csvBaselineLastFraction)],csvAdditionalDataLastFraction[2:length(csvAdditionalDataLastFraction)]),max(csvDataLastFraction[2:length(csvDataLastFraction)],csvBaselineLastFraction[2:length(csvBaselineLastFraction)],csvAdditionalDataLastFraction[2:length(csvAdditionalDataLastFraction)]))

boxplot(csvDataLastFraction[2:length(csvDataLastFraction)], border=c("red"), ylab = "@YAXIS_NAME@", ylim=limits)
boxplot(csvBaselineLastFraction[2], border=c("orange"),add=TRUE)
boxplot(csvAdditionalDataLastFraction[2], border=c("blue"),add=TRUE)

title(main="@TITLE_NAME@", cex.main=2)
par(fig = c(0, 1, 0, 1), oma = c(0, 0, 0, 0), mar = c(0, 0, 0, 0), new = TRUE)

plot(0, 0, type = "n", bty = "n", xaxt = "n", yaxt = "n")

legend("bottom", c("planned","with registration","variation"), lty=c(1,1,1), lwd=c(2,2,2),col=c("orange","blue","red"), cex = 1.2, bty = "n", horiz = TRUE, xpd = TRUE)


dev.off()