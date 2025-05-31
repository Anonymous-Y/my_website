---
title: 'Introduction to Panel Threshold Model'
date: 2016-05-28
permalink: /posts/2016-05-28-threshold
tags: 
  - Threshold Model
---
* These are my slides written for the graduate course of Intermediate Econometrics. The whole project is based on [Threshold effects in non-dynamic panels: Estimation, testing, and inference (Hansen, 1999)](http://www.sciencedirect.com/science/article/pii/S0304407699000251)  


* **Part One: Slides**  

Threshold Model Presentation Slides: [download](threshold_presentation.pdf)

* **Part Two: R code for this lecture**

First of all, we need to generate the data of y,x,n
```R
set.seed(123) # I set the seed for the sake of repeatability
e=rnorm(100,mean=0,sd=1)
x=rnorm(100,mean=0,sd=3^2)
n=1:100
y=rep(0,times=100)
y[1:50]=1+2*x[1:50]+e[1:50]
y[51:100]=1-2*x[51:100]+e[51:100]
data=data.frame(n,x,y,e)
```
Then we can plot out the relationship between y and n, as well as y and x.
```R
library(ggplot2)
p1=ggplot(data,aes(x=n,y=y))+geom_point()
p2=ggplot(data,aes(x=x,y=y))+geom_point()
p1
p2
```
Regression results
Suppose we do not aware the existance of thereshold effect
```R
reg1=lm(y~x,data)
summary(reg1)
```
If we know the thereshold and seprate the whole data frame into two groups,then conduct regressions separately.
```R
data1=subset(data, n<=50)
data2=subset(data,n>50)
reg2=lm(y~x,data1)
reg3=lm(y~x,data2)
summary(reg2)
summary(reg3)
```
If we do not know where the thereshold is, then what shoudl we do?
```R
reg=list()
rss=array()
for (i in 1:99)
{
  dum=x
  dum[(i+1):100]=0
  reg[[i]]=lm(y~x+dum)
  rss[i]=sum(residuals(reg[[i]])^2)
}
order(rss)

Rss=data.frame(n=1:99,rss)
ggplot(Rss,aes(x=n,y=rss))+geom_point()
```
Now if we have two theresholds, we can still use nested loop to discern these two theresholds. However Hensen proposed a more elegant solution.
Prepare the data:
```R
set.seed(456) # I set the seed for the sake of repeatability
e=rnorm(100,mean=0,sd=1)
x=rnorm(100,mean=0,sd=3^2)
n=1:100
y=rep(0,times=100)
y[1:30]=1+2*x[1:30]+e[1:30]
y[31:60]=1-2*x[31:60]+e[31:60]
y[61:100]=1+4*x[61:100]+e[61:100]
data=data.frame(n,x,y,e)
```
Then we can plot out the relationship between y and n, as well as y and x.
```R
library(ggplot2)
p1=ggplot(data,aes(x=n,y=y))+geom_point()
p2=ggplot(data,aes(x=x,y=y))+geom_point()
p1
p2
```
Now we use the method proposed by Hensen to discern theresholds.
Pinpoint the first thereshold:
```R
reg=list()
rss1=array()
for (i in 1:99)
{
  dum=x
  dum[(i+1):100]=0
  reg[[i]]=lm(y~x+dum)
  rss1[i]=sum(residuals(reg[[i]])^2)
}
which.min(rss1)
#plot the figure
Rss1=data.frame(n=1:99,rss1)
ggplot(Rss1,aes(x=n,y=rss1))+geom_point()
```
Pinpoint the second thereshold
```R
reg2=list()
rss2=array()
for(i in 1:99)
{
  dum1=x
  dum2=x
  left=min(i,which.min(rss1))
  right=max(i,which.min(rss1))
  dum1[(left+1):100]=0
  dum2[1:right]=0
  reg2[[i]]=lm(y~x+dum1+dum2)
  rss2[i]=sum(residuals(reg2[[i]])^2)
}
which.min(rss2)
#plot the figure
Rss2=data.frame(n=1:99,rss2)
ggplot(Rss2,aes(x=n,y=rss2))+geom_point()
```
Pinpoint the first thereshold again
```R
reg3=list()
rss3=array()
for(i in 1:99)
{
  dum1=x
  dum2=x
  left=min(i,which.min(rss2))
  right=max(i,which.min(rss2))
  dum1[(left+1):100]=0
  dum2[1:right]=0
  reg3[[i]]=lm(y~x+dum1+dum2)
  rss3[i]=sum(residuals(reg3[[i]])^2)
}
which.min(rss3)
#plot the figure
Rss3=data.frame(n=1:99,rss3)
ggplot(Rss3,aes(x=n,y=rss3))+geom_point()
```
put those aboving figures into one picture.
```R
all=rbind(data.frame(n=1:99,rss=rss1,t="loop 1"),data.frame(n=1:99,rss=rss2,t="loop 2"),data.frame(n=1:99,rss=rss3,t="loop 3"))
p=ggplot(all, aes(x=n,y=rss))
p+geom_path(aes(position=t,color=t))+geom_point(aes(position=t,color=t))
```
Bootstrap, in this case, we only consider one threshold.
```R
set.seed(123) # I set the seed for the sake of repeatability
e=rnorm(100,mean=0,sd=1)
x=rnorm(100,mean=0,sd=3^2)
n=1:100
y=rep(0,times=100)
y[1:50]=1+2*x[1:50]+e[1:50]
y[51:100]=1-2*x[51:100]+e[51:100]
data=data.frame(n,x,y,e)

breg1=lm(y~x,data)
s0=sum(residuals(breg1)^2)
library(boot)
fvalue=function(data,indices){
  d=data[indices,]
  bregloop=list()
  brss=array()
  for (i in 1:99)
  {
    dum=d$x
    dum[(i+1):100]=0
    bregloop[[i]]=lm(y~x+dum,data=d)
    brss[i]=sum(residuals(bregloop[[i]])^2)
  }
  a=which.min(brss)
  dum=d$x
  dum[(a+1):100]=0
  breg2=lm(y~x+dum,data=d)
  s1=sum(residuals(breg2)^2)
  f=(s0/s1-1)*(100-1)
  return(f)
}

result=boot(data=data,fvalue,R=99)
f=result$t
result=boot(data=data,fvalue,R=99,formula1=y~x+dum)
f=result$t
```

The real f0
```R
dum=data$x
dum[51:100]=0
reg4=lm(y~x+dum,data)
rss4=sum(residuals(reg4)^2)
f0=(s0/rss4-1)*(100-1)

table(f>f0) # so the p-value=0, we should reject H0
```
Last question, get the confidence intervals for gamma
```R
LR=(rss-rss4)/(rss4/(100-1))
order(LR)
c=-2*log(1-sqrt(1-0.01)) #we set the asymptotic level alpha at 1%
LR[LR<c]
```
