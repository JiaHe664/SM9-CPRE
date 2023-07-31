
import binascii
from math import ceil, floor, log
from gmssl.sm3 import sm3_kdf, sm3_hash
from random import SystemRandom
import gmssl.optimized_field_elements as fq
import gmssl.optimized_curve as ec
import gmssl.optimized_pairing as ate
import secrets


FAILURE = False
SUCCESS = True
PRIME=6864797660130609714981900799081393217269435300143305409394463459185543183397656052122559640661454554977296311391480858037121987999716643812574028291115057151

def bitlen (n):
    return floor (log(n,2) + 1)

def i2sp (m, l):
    format_m = ('%x' % m).zfill(l*2).encode('utf-8')
    octets = [j for j in binascii.a2b_hex(format_m)]
    octets = octets[0:l]
    return ''.join (['%02x' %oc for oc in octets])

def fe2sp (fe):
    fe_str = ''.join (['%x' %c for c in fe.coeffs])
    if (len(fe_str) % 2) == 1:
        fe_str = '0' + fe_str
    return fe_str

def ec2sp (P):
    ec_str = ''.join([fe2sp(fe) for fe in P])
    return ec_str

def str2hexbytes (str_in):
    return [b for b in str_in.encode ('utf-8')]

def h2rf (i, z, n):
    l = 8 * ceil ((5*bitlen(n)) / 32)
    msg = i2sp(i,1).encode('utf-8')
    ha = sm3_kdf (msg+z, l)
    h = int (ha, 16)
    return (h % (n-1)) + 1

def setup ():
    P1 = ec.G2
    P2 = ec.G1
    
    return (P1, P2)

def keygen(pp):

    P1, P2 = pp
    rand_gen = SystemRandom()
    s = rand_gen.randrange(ec.curve_order)
    pk_1 = ec.multiply (P1, s)
    pk_2 = ec.multiply(P2, s)
    pk = (pk_1, pk_2)
    sk = s

    return (sk, pk)

def enc(pp, pk, msg, proxy_cond, mac_key_len):

    P1, P2 = pp
    pk_1, pk_2 = pk

    hex_msg = str2hexbytes (msg)
    mbytes = len(hex_msg)
    mbits = mbytes * 8
    
    k, C1 = kem_encap (pp, pk_1, proxy_cond, mbits + mac_key_len)
    k = str2hexbytes (k)
    k1 = k[:mbytes]
    k2 = k[mbytes:]

    C2 = []
    for i in range (mbytes):
        C2.append (hex_msg[i] ^ k1[i])

    hash_input = C2 + k2
    C3 = sm3_hash(hash_input)[:int(mac_key_len/8)]

    

    return (C1, C2, C3)

def rkeygen(proxy_cond, sk_A, pk_B):

    pk_1, pk_2 = pk_B

    proxy_cond_hash = sm3_hash (str2hexbytes (proxy_cond))
    m = h2rf (1, (proxy_cond_hash + '01').encode('utf-8'), ec.curve_order)
    m = sk_A + m
    if (m % ec.curve_order) == 0:
        return FAILURE
    m = sk_A * fq.prime_field_inv (m, ec.curve_order)
    rk_A2B = ec.multiply (pk_2, m)

    return (rk_A2B, m)

def blind_secret(secret, pk_B):

    pk_1, pk_2 = pk_B

    rand_gen = SystemRandom()
    blind_factor = rand_gen.randrange(ec.curve_order)
    P = ec.multiply (pk_2, blind_factor)
    blind_key = ec.neg(P)
    blind_secret = secret + blind_factor

    return (blind_secret, blind_key)

def unblind(blind_rk, blind_key):

    rk = ec.add(blind_rk, blind_key)

    return rk


def arithmetic_share(secret, total_shares, pk):
    pk_1, pk_2 = pk
    rk_shares = []
    sum = secret
    for i in range(total_shares-1):
        rand_gen = SystemRandom()
        x = rand_gen.randrange(ec.curve_order)
        sum -= x
        rk_share = ec.multiply(pk_2, x)
        rk_shares.append(rk_share)
    rk_shares.append(ec.multiply(pk_2, sum))
    
    return rk_shares

# def shamir_share(secret, threshold, total_shares):
#     # First, generate t random numbers, with the secret at poly(0)
#     poly = [secrets.randbelow(PRIME) for t in range(threshold)]
#     poly[0] = secret

#     # Next, we evaluate the polynomial at x \in {1..t}
#     # (skip x=0, as that is secret)
#     shares = [
#         (x, _evaluate(poly, x, PRIME))
#             for x in range(total_shares + 1)
#     ]

#     return shares[1:]

def shamir_share(secret, threshold, total_shares, pk_B):
    # First, generate t random numbers, with the secret at poly(0)
    poly = [secrets.randbelow(PRIME) for t in range(threshold)]
    poly[0] = secret

    # Next, we evaluate the polynomial at x \in {1..t}
    # (skip x=0, as that is secret)
    shares = [
        (x, _evaluate(poly, x, PRIME))
            for x in range(total_shares + 1)
    ]

    pk_1, pk_2 = pk_B

    rk_shares = [(x_j, ec.multiply(pk_2, y_j)) for x_j, y_j in shares[1:]]

    return rk_shares

def shamir_recon(share, recon_set):
    acc = 1
    x_j, y_j = share
    for x in recon_set:
        if x != x_j:
            dem = (x - x_j) % PRIME
            div = _div_mod(x, dem, PRIME)
            acc = (acc * div) % PRIME 

    partial_rk = ec.multiply (y_j, acc)   

    return partial_rk  

# def shamir_recon(recon_shares, pk_B):

#     pk_1, pk_2 = pk_B
#     if len(recon_shares) == 1:
#         # If there's one share, then shares[0] == secret
#         return None
#     secret = _interpolate(recon_shares, PRIME) 

#     return ec.multiply(pk_2, secret)

def aggregate_ct(partial_cts):

    C1, C2, C3, C4 = partial_cts[0]
    agg_res = C4
    for partial_ct in partial_cts[1:]:
        C1, C2, C3, C4 = partial_ct
        agg_res *= C4

    return (C1, C2, C3, agg_res)

def _interpolate(shares, prime):
    secret = 0
    for x_j, y_j in shares:
        l_j = _lagrange_poly_at(x_j, shares, prime)
        secret = (secret + ((y_j * l_j) % prime)) % prime
    return secret

def _lagrange_poly_at(x_j, xs, prime):
    acc = 1
    for x, _ in xs:
        if x != x_j:
            dem = (x - x_j) % prime
            div = _div_mod(x, dem, prime)
            acc = (acc * div) % prime
    return acc


# Since (n / m) is n * 1/m, (n / m) mod p is n * m^-1 mod p
def _div_mod(n, m, prime):
    return (n * _inverse(m, prime)) % prime

# Implementation taken from
# https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm#Modular_integers
def _inverse(m, p):
    (t, new_t) = (0, 1)
    (r, new_r) = (p, m)
    while new_r != 0:
        quot = r // new_r
        (t, new_t) = (new_t, t - (quot * new_t))
        (r, new_r) = (new_r, r - (quot * new_r))

    if t < 0:
        t += p

    return t % p


def _evaluate(poly, x, prime):
    res = 0
    for coeff in reversed(poly):
        res = (res * x) % prime
        res = (res + coeff) % prime
    return res

def reenc(rk_A2B, ct_A):

    C1, C2, C3 = ct_A

    if ec.is_on_curve (C1, ec.b2) == False:
        return FAILURE

    C4 = ate.pairing (C1, rk_A2B)
        
    return (C1, C2, C3, C4)

def dec_1(pp, sk, ct, proxy_cond, mac_key_len):
    C1, C2, C3 = ct

    mbytes = len(C2)
    l = mbytes*8 + mac_key_len
    D = private_key_extract(pp, sk, proxy_cond)
    k = kem_decap_1(proxy_cond, sk, C1, D, l)
    k = str2hexbytes (k)
    k1 = k[:mbytes]
    k2 = k[mbytes:]

    hash_input = C2 + k2
    C3prime = sm3_hash(hash_input)[:int(mac_key_len/8)]

    if C3 != C3prime:
        return FAILURE
    
    pt = []
    for i in range (mbytes):
        pt.append (chr (C2[i] ^ k1[i]))

    message = ''.join(pt)
        
    return message

def private_key_extract (pp, sk, proxy_cond):
    P1, P2 = pp

    proxy_cond_hash = sm3_hash (str2hexbytes (proxy_cond))
    m = h2rf (1, (proxy_cond_hash + '01').encode('utf-8'), ec.curve_order)
    m = sk + m
    if (m % ec.curve_order) == 0:
        return FAILURE
    m = sk * fq.prime_field_inv (m, ec.curve_order)

    Da = ec.multiply (P2, m)
    
    return Da

def dec_2(sk, ct, proxy_cond, mac_key_len,):

    C1, C2, C3, C4 = ct

    mbytes = len(C2)
    l = mbytes*8 + mac_key_len
    k = kem_decap_2(proxy_cond, sk, C1, C4, l)
    k = str2hexbytes (k)
    k1 = k[:mbytes]
    k2 = k[mbytes:]

    hash_input = C2 + k2
    C3prime = sm3_hash(hash_input)[:int(mac_key_len/8)]

    if C3 != C3prime:
        return FAILURE
    
    pt = []
    for i in range (mbytes):
        pt.append (chr (C2[i] ^ k1[i]))

    message = ''.join(pt)
        
    return message

def public_key_extract (P1, pk_1, proxy_cond):
    
    proxy_cond_hash = sm3_hash (str2hexbytes (proxy_cond))
    h1 = h2rf (1, (proxy_cond_hash + '01').encode('utf-8'), ec.curve_order)

    Q = ec.multiply (P1, h1)
    Q = ec.add (Q, pk_1)

    return Q

# encrypt

def kem_encap (pp, pk_1, proxy_cond, l):

    P1, P2 = pp

    Q = public_key_extract (P1, pk_1, proxy_cond)

    rand_gen = SystemRandom()
    x = rand_gen.randrange (ec.curve_order)

    C1 = ec.multiply (Q, x)
    g = ate.pairing (pk_1, P2)
    t = g**x

    proxy_cond_hash = sm3_hash (str2hexbytes (proxy_cond))
    kdf_input = ec2sp(C1) + fe2sp(t) + proxy_cond_hash
    k = sm3_kdf (kdf_input.encode ('utf-8'), l)

    return (k, C1)

def kem_decap_2 (proxy_cond, sk, C1, C4, l):
    if ec.is_on_curve (C1, ec.b2) == False:
        return FAILURE

    t = C4**(fq.prime_field_inv (sk, ec.curve_order))

    proxy_cond_hash = sm3_hash (str2hexbytes (proxy_cond))
    kdf_input = ec2sp(C1) + fe2sp(t) + proxy_cond_hash
    k = sm3_kdf (kdf_input.encode ('utf-8'), l)

    return k

def kem_decap_1 (proxy_cond, sk, C1, D, l):

    if ec.is_on_curve (C1, ec.b2) == False:
        return FAILURE

    t = ate.pairing (C1, D)

    uid = sm3_hash (str2hexbytes (proxy_cond))
    kdf_input = ec2sp(C1) + fe2sp(t) + uid
    k = sm3_kdf (kdf_input.encode ('utf-8'), l)

    return k

