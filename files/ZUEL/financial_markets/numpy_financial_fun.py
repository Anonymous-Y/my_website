import numpy_financial as npf
import numpy as np

# manual: https://numpy.org/numpy-financial/latest/index.html

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
term=10
pmt=100
fv=1000
r= 0.1
pv=npf.pv(r, term, pmt, fv)
np.round(pv, 2)

term=9
pmt=100
fv=1000
r= 0.2
pv=npf.pv(r, term, pmt, fv)
np.round(pv, 2)