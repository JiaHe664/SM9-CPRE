import secrets

PRIME=6864797660130609714981900799081393217269435300143305409394463459185543183397656052122559640661454554977296311391480858037121987999716643812574028291115057151
def encrypt(secret, threshold, total_shares):
    # First, generate t random numbers, with the secret at poly(0)
    poly = [secrets.randbelow(PRIME) for t in range(threshold)]
    poly[0] = secret

    # Next, we evaluate the polynomial at x \in {1..t}
    # (skip x=0, as that is secret)
    shares = [
        (x, _evaluate(poly, x, PRIME))
            for x in range(total_shares + 1)
    ]

    # Skip the secret
    return shares[1:]

def _evaluate(poly, x, prime):
    res = 0
    for coeff in reversed(poly):
        res = (res * x) % prime
        res = (res + coeff) % prime
    return res

def decrypt(shares):
    if len(shares) == 1:
        # If there's one share, then shares[0] == secret
        return None

    return _interpolate(shares, PRIME)

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

if __name__ == '__main__':
    
    secret = 221341769519005074251305408305571765846150129886068028997738422867924873286038952879269561520728074418106793506574784865374502483602380076405654604187334
    threshold = 20
    total_shares = 100
    print(secret)

    shares = encrypt(secret, threshold, total_shares)

    recon_secret = decrypt(shares[20:20+threshold])
    print(recon_secret)