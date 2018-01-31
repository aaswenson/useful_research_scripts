MCNP6 leakage study radius:0.5 cm, height:25 cm. 
c Cell Card
1 3 -0.08713 -1 4 -5 imp:n=1   $ coolant channel
2 2 -19.25 1 -2 4 -5 imp:n=1 $ cladding
3 1 -14.48 -3 2 4 -5 imp:n=1 $ fuel
99 0 5:-4:(3 -5 4) imp:n=0  $ outside world
 
c Surface Card
1 CZ 0.5
2 CZ 0.531
3+ rhp 0 0 -10000 0 0 100000 1.593 0
4 PZ -12.5
5 PZ 12.5

c Data Card
m1
     7014 4.9805e-01
     7015 1.9491e-03
     92235 4.9995e-01
     92238 4.9369e-05
C name: Tungsten
C density = 19.2
m2
     74180 1.2000e-03
     74182 2.6500e-01
     74183 1.4310e-01
     74184 3.0640e-01
     74186 2.8430e-01
C density = 0.1
m3
     6012 3.3022e-01
     6013 3.5715e-03
     8016 6.6596e-01
     8017 2.5368e-04
kcode 1 1 1 1
ksrc  1 1 1
     -1 -1 -1 
     1 -1 1
     -1 1 1
     1 1 -1
mode n
print
