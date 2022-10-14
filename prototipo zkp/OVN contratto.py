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

def euclid(a, b):
    s1, s2 = 1, 0
    t1, t2 = 0, 1
    while b != 0:
        quotient, remainder = a/b, a%b
        a = b
        b = remainder
        s1, s2 = s2, s1 - quotient * s2
        t1, t2 = t2, t1 - quotient * t2
    return a, s1, t1

def inverso_mod(a, mod):
    _, _, res = euclid(mod, a)
    return res % mod

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
    check1 = (chal == ((d1 + d2) % q))
    check2 = (a1 == ((pow(gen, r1, p) * pow(commit, d1, p)) % p))
    check3 = (a2 == ((pow(gen, r2, p) * pow(commit, d2, p)) % p))
    # print(a2, pow(g,r2, p), pow(commit,d2, p), ( (pow(g,r2, p) * pow(commit, d2, p)) %p) )

    check4 = (b1 == ((pow(key, r1, p) * pow(voto, d1, p)) % p))
    check5 = (b2 == ((pow(key, r2, p) * pow(voto, d2, p) * pow(inverso_mod(p, gen), d2, p)) % p))
    print(check1, check2, check3, check4, check5)
    if (check1 and check2 and check3 and check4 and check5):
        voti[i] = voto
        return True
    else:
        return False
