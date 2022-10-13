from random import *
import hashlib


def hash(g):
    return g


"""Global parameters"""
# p =2**64 - 363; q = 14924550221447857
p = 9547804857313097087  # prime 2^63 bit
q = 4773902428656548543  # prime 2^62 bit
g = 27
#q= 13

"""Parte fatta in autonomia da un partecipante"""
x = randint(1, q - 1)
gX = pow(g, x, p)
rnd = randint(1, q - 1)
gRnd = pow(g, rnd, p)
xChal = int(hashlib.sha256(str([g, gX, gRnd]).encode('utf-8')).hexdigest(), 16) % q
xProof = (rnd - xChal * x) % (q)
""" Vengono mandate al contratto gX, gRnd, xProof"""

"""Verifica all'interno dello smart contract"""


# occorre definire un metodo di calcolo per le potenze modulo q,
# Attenzione agli overflow
def verify(claim, claimRnd, proof):
    chal = int(hashlib.sha256(str([g, claim, claimRnd]).encode('utf-8')).hexdigest(), 16) % q
    return (((pow(g, proof, p) * pow(claim, chal, p)) % p) == claimRnd)


print(verify(gX, gRnd, xProof))

"""ROUND 2"""
""" Un partecipante chiede al contratto gX1, ..., gXn mandati dagli altri"""
"""Esempio con 3 partecipanti, x,y,z """
y = randint(1, q - 1)
gY = pow(g, y, p)
z = randint(1, q - 1)
gZ = pow(g, z, p)



"""Funzioni per invertire modulo q"""
def euclid(a, b):
    s1, s2 = 1, 0
    t1, t2 = 0, 1
    while b != 0:
        quotient, remainder = divmod(a, b)
        a = b
        b = remainder
        s1, s2 = s2, s1 - quotient * s2
        t1, t2 = t2, t1 - quotient * t2
    return a, s1, t1

def inverso_mod(a, b):
    _, _, res = euclid(a, b)
    return res % a

"""Calcolo chiavi di voto"""
xKey = (inverso_mod(p, gY) * inverso_mod(p, gZ) ) % p
yKey = ( gX * inverso_mod(p, gZ) ) % p
zKey = ( gX * gY ) %p



"""Primo partecipante vota SI (v = 1), e crea la ZKP """
xVoto = (pow( xKey, x , p) * g ) % p
wRndX, rRndX, dRndX = randint(1,q-1) ,randint(1,q-1),randint(1,q-1)
a1X = (pow(g,rRndX, p) * pow(gX, dRndX, p) )%p
b1X = (pow(xKey, rRndX, p)* pow(xVoto, dRndX, p) )%p
a2X = pow(g, wRndX,p) %p
b2X = pow(xKey, wRndX, p) %p

xChalVoto = int(hashlib.sha256(str([gX, xKey, xVoto, a1X, b1X, a2X, b2X]).encode('utf-8')).hexdigest(), 16) % q

d2X = (xChalVoto - dRndX ) %q
r2X = (wRndX - (x * d2X) ) %q

"""Il certificato ZKR consiste in [dRndX, rRndX, d2X, r2X]"""

def verify_voto( commit, key, voto, a1, b1, a2, b2, d1, r1,d2,r2):
    chal = int(hashlib.sha256(str([commit, key, voto, a1, b1, a2, b2]).encode('utf-8')).hexdigest(), 16) % q
    check1 = ( chal == ((d1 + d2) % q) )
    check2 = ( a1 == ( ( pow(g,r1, p) * pow(commit, d1, p)) %p))
    check3 = ( a2 == ( (pow(g,r2, p) * pow(commit, d2, p)) %p))
    #print(a2, pow(g,r2, p), pow(commit,d2, p), ( (pow(g,r2, p) * pow(commit, d2, p)) %p) )

    check4 = (b1 == ( (pow(key, r1, p ) * pow(voto, d1, p)) %p))
    check5 = (b2 == ( (pow(key, r2, p ) * pow(voto, d2, p) *pow(inverso_mod(p, g),d2,p)) %p))
    print(check1,check2,check3,check4,check5)
    return (check1 and check2 and check3 and check4 and check5)

print(verify_voto(gX,xKey, xVoto, a1X,b1X,a2X, b2X, dRndX,rRndX,d2X,r2X))

"""Secondo partecipante vota NO (v= 0) e crea la ZKP (diversa)"""
yVoto = (pow( yKey, y , p) ) % p
wRndY, rRndY, dRndY = randint(1,q-1) ,randint(1,q-1),randint(1,q-1)
a1Y = pow(g, wRndY,p) %p
b1Y = pow(yKey, wRndY, p) %p
a2Y =  (pow( g, rRndY, p) * pow(gY, dRndY, p) )%p
b2Y = (pow(yKey, rRndY, p)* pow( ( yVoto* inverso_mod(p,g)), dRndY, p) )%p

yChalVoto = int(hashlib.sha256(str([gY, yKey, yVoto, a1Y, b1Y, a2Y, b2Y]).encode('utf-8')).hexdigest(), 16) % q

d2Y = (yChalVoto - dRndY ) %q
r2Y = (wRndY - (y * d2Y) ) %q
print(verify_voto(gY,yKey, yVoto, a1Y,b1Y,a2Y, b2Y,d2Y,r2Y,dRndY,rRndY))

"""Terzo voto SI, senza ZKP """
zVoto = (pow( zKey, z , p) * g ) % p


""" Conteggio voti """

def conteggio():
    tot = (xVoto * yVoto * zVoto) % p
    for i in range (0,4):
        check = ( tot == pow(g, i, p) )
        print (tot, pow(g,i , p))
        if check:
            return i

print ( conteggio() )