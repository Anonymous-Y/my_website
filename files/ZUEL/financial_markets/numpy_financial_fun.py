import numpy_financial as npf
import numpy as np

# manual: https://numpy.org/numpy-financial/latest/index.html

####################################################################
# Lecture 2

# Fixed-Payment Loan Example
pv=100000
r=0.07
term=20
pmt=npf.pmt(r, term, pv)
round(-pmt, 2)

# calculate the yield to maturity
pv=100000
term=20
pmt=-9439.29  #remember your pmt should be negative 
fv=0
rate=npf.rate(term, pmt, pv,fv)
round(rate,2)


# Counpon Bond Example
term=8
pmt=100
fv=1000
r=0.1225
pv=npf.pv(r, term, pmt, fv)
round(pv, 2)


# calculate Table 1
term=10
pmt=100
fv=1000
r=np.array([0.0713, 0.0848, 0.1, 0.1175, 0.1381])
pv=npf.pv(r, term, pmt, fv)
np.round(pv, 2)


# Example: the rate of return
term=9
pmt=100
fv=1000
r= 0.2
pv=npf.pv(r, term, pmt, fv)
np.round(pv, 2)

term=20
pmt=4000
fv=0
r= 0.02
pv=npf.pv(r, term, pmt, fv)
np.round(pv, 2)

################################################
# Lecture 11

# calculate the monthly payment 
def mth_pay(pv, r, term):
    pmt=npf.pmt(r, term, pv)
    return pmt

mth_pay(100000, 0.12/12, 360)  # without paying discount points
mth_pay(100000, 0.115/12, 360)  # pay 2% discount points

# calcualte the effective annual rate after paying the 2% discount points
pv = 98000
pmt = -990.29
term = 360
fv = 0
rate=npf.rate(term, pmt, pv,fv)
rate = round(rate,6)
# effective annual rate
((1+rate)**12 - 1) *100

# let us make a function to calculate the effective annual rate for different terms
def effect_rate(pv, r, term, dis_pt=0.02, fv=0):
    pmt = mth_pay(pv, r, term)
    rate=npf.rate(term, pmt, pv*(1-dis_pt), fv)
    rate = round(rate,6)
    # effective annual rate
    er=((1+rate)**12 - 1) *100
    return er

# 30 years
effect_rate(pv=100000, r=0.115/12, term=360)
# 15 years
effect_rate(pv=100000, r=0.115/12, term=12*15)


terms = list(range(1, 11)) + [15, 30]
for item in terms:
    print(item, ' years: ', effect_rate(pv=100000, r=0.115/12, term=12*item), '\n')

# when the present value of the savings (1028.61-990.29 = $38.32) equals the $2,000 upfront
npf.nper(rate=0.12/12, pmt=38.32, pv=-2000)