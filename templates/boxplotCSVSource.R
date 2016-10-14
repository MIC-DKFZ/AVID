setwd("@WORKING_DIRECTORY@")
csvData <- read.csv("@CSVDATA_FILE@", header=0, sep=";", as.is=TRUE)
csvBaseline <- read.csv("@CSVBASELINE_FILE@", header=0, sep=";", as.is=TRUE)
png(file="@PNG_FILE@", height=500, width=500)

csvDataLastFraction = csvData[,dim(csvData)[2]]
csvBaselineLastFraction = csvBaseline[,dim(csvBaseline)[2]]

boxplot(csvDataLastFraction[2:length(csvDataLastFraction)], border=c("red"), ylab = "Gy", ylim=c(min(csvDataLastFraction[2:length(csvDataLastFraction)],csvBaselineLastFraction[2:length(csvBaselineLastFraction)]),max(csvDataLastFraction[2:length(csvDataLastFraction)],csvBaselineLastFraction[2:length(csvBaselineLastFraction)])))
boxplot(csvBaselineLastFraction[2], border=c("orange"),add=TRUE)

dev.off()