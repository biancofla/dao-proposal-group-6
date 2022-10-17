from random import *
import hashlib

"""Global parameters"""
# p =2**64 - 363; q = 14924550221447857
p = 9547804857313097087  # prime 2^63 bit
q = 4773902428656548543  # prime 2^62 bit
g = 27
#q= 13
"""Al momento dell'attivazione riceve un numero i"""
i =3
n = 5 #totale partecipanti

"""Parte fatta in autonomia da un partecipante per il round 1"""
x = randint(1, q - 1)
gX = pow(g, x, p) # ID
rnd = randint(1, q - 1)
gRnd = pow(g, rnd, p)
xChal = int(hashlib.sha256(str([g, i, gX, gRnd]).encode('utf-8')).hexdigest(), 16) % q
xProof = (rnd - xChal * x) % (q)
"""Fa calcolare al contratto verifyR1( i, gX, xChal, xProof)"""

"""Dopo che tutti hanno fatto il round 1, si recupera i loro valore gX1, gX2, ..., gXn, e li salva in un vettore"""
id = [randint(1, p) for i in range(0,n)]
votingKey = 1
for i in range(0,i):
    votingKey = (votingKey* id[i])%p
for i in range(i+1, n):
    votingKey = (votingKey * pow(id[i], -1, p) ) %p

votingKey = pow(votingKey, x, p)


"""Per votare v=1 (sì) """
xVoto = (pow( votingKey, x , p) * g ) % p
wRndX, rRndX, dRndX = randint(1,q-1) ,randint(1,q-1),randint(1,q-1)
a1X = (pow(g,rRndX, p) * pow(gX, dRndX, p) )%p
b1X = (pow(votingKey, rRndX, p)* pow(xVoto, dRndX, p) )%p
a2X = pow(g, wRndX,p) %p
b2X = pow(votingKey, wRndX, p) %p
xChalVoto = int(hashlib.sha256(str([i,gX,votingKey, xVoto, a1X, b1X, a2X, b2X]).encode('utf-8')).hexdigest(), 16) % q
d2X = (xChalVoto - dRndX ) %q
r2X = (wRndX - (x * d2X) ) %q
"""Fa calcolare al contratto verifyR2( i,gX, votingKey, xVoto, a1X, b1X, a2X, b2X, dRndX, rRndX, d2X, r2X)"""

"""Per votare v= 0 (no) """
xVoto = (pow( votingKey, x , p) ) % p
wRndX, rRndX, dRndX = randint(1,q-1) ,randint(1,q-1),randint(1,q-1)
a1X = pow(g, wRndX,p) %p
b1X = pow(votingKey, wRndX, p) %p
a2X =  (pow( g, rRndX, p) * pow(gX, dRndX, p) )%p
b2X = (pow(votingKey, rRndX, p)* pow( (xVoto* pow(g,-1,p)), dRndX, p) )%p

yChalVoto = int(hashlib.sha256(str([i,gX, votingKey, xVoto, a1X, b1X, a2X, b2X]).encode('utf-8')).hexdigest(), 16) % q

d2X = (yChalVoto - dRndX ) %q
r2X = (wRndX - (x * d2X) ) %q
""" Fa calcolare al contratto verifyR2(i,gX,votingKey, xVoto, a1X,b1X,a2X, b2X,d2X,r2X,dRndX,rRndX))"""
"""NOTA le ultime due sono scambiate rispetto a prima"""
