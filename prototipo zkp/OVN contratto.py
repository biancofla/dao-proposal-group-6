from random import*
import hashlib
"""Parametri globali"""
p = 9547804857313097087  # prime 2^63 bit
q = 4773902428656548543  # prime 2^62 bit
gen = 27
n= 5 #numero partecipanti
id = [0 for i in range(0,n)]# vettore contenente le identita' gen^x
voti = [0 for i in range(0,n)] #vettore contenente i voti
print(id)
"""Due variabile scratch per i conti """
tmp = 0
res = 0

""" Da definire  somma, moltiplicazione,ed esponenziale senza che vada in overflow"""
"""Qui assumiamo mod > 2**32"""
def sub_mod(a, b, mod):
    if a>=b:
        return a-b
    else:
        return mod - b +a
def add_mod( a,b,mod):
    if b==0:
        return a
    #Quanto segue equivale a fare sub_mod(a, b-mod, mod), ma non fa la chiamata alla subroutine
    b = mod - b
    if a >= b:
        return a - b
    else:
        return mod - b + a
def mult_mod(a,b, mod):
    if a< 2**32:
        if b < 2**32:
            return (a*b) % mod
        else:
            return (mod -  ( (a*(mod-b)) % mod) )
    else:
        if b< 2**32:
            return mod - ( (( mod-a)*b) % mod )
        else:
            return ((mod - a)*(mod -b ) )% mod

def pow_mod(base, exp, mod):
    res = 1
    if exp==0 :
        return res
    while exp > 0:
        if (exp %2) == 1:
            res = mult_mod(res, base, mod)
        else:
            base = mult_mod(base, base, mod)
        exp = exp>>1
        print(res)
    return mult_mod(res,base, mod)

def inverso_mod(b,mod):
    a= mod
    t1, t2 = 0, 1
    segnoT1, segnoT2 = 1, 1
    while b != 0:
        quotient, remainder = a//b, a%b
        a = b
        b = remainder
        tmp, segnoTmp = t2, segnoT2
        if segnoT1 == segnoT2:
            if t1 >= quotient * t2:
                t2 = t1 - quotient * t2
            else:
                t2 = quotient * t2 - t1
                segnoT2 = segnoT2 ^ 1  # xor per cambiare segno
        else:
            t2 = t1 + quotient * t2
            segnoT2 = segnoT2 ^ 1
        t1, segnoT1 = tmp, segnoTmp
    if segnoT1 == 0:
        return mod-t1
    else:
        return t1

"""Funzione chiamata con i parametri passati dal partecipante
   Verifica che il partecipante i-esimo effettivamente conosce un segreto x_i
   Successivamente salva il valore di claimId come identità dell' i-esimo partecipante """
def verifyR1(i,claimId, claimRnd, proof):
    chal = int(hashlib.sha256(str([gen,i, claimId, claimRnd]).encode('utf-8')).hexdigest(), 16) % q
    if (mult_mod(pow_mod(gen, proof, p) , pow_mod(claimId, chal, p), p) == claimRnd):
        id[i] = claimId
        return True
    else:
        return False

def verifyR2(i,commit, key, voto, a1, b1, a2, b2, d1, r1, d2, r2):
    chal = int(hashlib.sha256(str([i,commit, key, voto, a1, b1, a2, b2]).encode('utf-8')).hexdigest(), 16) % q
    check1 = (chal == add_mod(d1 ,d2, q) )
    check2 = (a1 == mult_mod( pow_mod(gen, r1, p) , pow_mod(commit, d1, p) , p) )
    check3 = (a2 == mult_mod(pow_mod(gen, r2, p), pow_mod(commit, d2, p),p))
    check4 = (b1 == mult_mod(pow_mod(key, r1, p), pow_mod(voto, d1, p), p))
    check5 = (b2 == mult_mod(pow_mod(key, r2, p) , pow_mod(mult_mod(voto,inverso_mod(gen,p),p), d2, p) , p))
    print(check1, check2, check3, check4, check5)
    if (check1 and check2 and check3 and check4 and check5):
        voti[i] = voto
        return True
    else:
        return False

def conta_voti():
    tot =1
    for i in range(0,n):
        tot = mult_mod(tot, voti[i],p)

    testTot = 1
    if (testTot == tot):
        return 0
    for j in range(0,n):
        testTot = mult_mod(testTot, gen, p)
        if testTot == tot:
            return j+1