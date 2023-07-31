from gmssl import cpre_sm9
import random
import time

RUN_TIMES = 100

if __name__ == '__main__':

    run_time = 0
    for i in range(RUN_TIMES):
        start_time = time.clock()
        pp = cpre_sm9.setup ()     # get the public params
        end_time = time.clock()
        run_time += end_time - start_time
    print('cpre-setup: %s ms' % (((run_time)*1000)/RUN_TIMES)) 

    # pp = cpre_sm9.setup ()     # get the public params

    # initial users' (pk,sk)
    run_time = 0
    for i in range(RUN_TIMES):
        start_time = time.clock()
        sk_A, pk_A = cpre_sm9.keygen(pp)    # user A's key pair
        end_time = time.clock()
        run_time += end_time - start_time
    print('cpre-keygen: %s ms' % (((run_time)*1000)/RUN_TIMES)) 

    # sk_A, pk_A = cpre_sm9.keygen(pp)    # user A's key pair
    sk_B, pk_B = cpre_sm9.keygen(pp)    # user B's key pair
    
    # user A run cpre-enc
    msg = 'hello, zsh!hello, zsh!hello, zsh'
    proxy_cond = 'greet'

    run_time = 0
    for i in range(RUN_TIMES):
        start_time = time.clock()
        ct_A =  cpre_sm9.enc(pp, pk_A, msg, proxy_cond, 32)
        end_time = time.clock()
        run_time += end_time - start_time
    print('cpre-encrypt: %s ms' % (((run_time)*1000)/RUN_TIMES)) 

    # user A run origin-dec

    run_time = 0
    for i in range(RUN_TIMES):
        start_time = time.clock()
        tmp =  cpre_sm9.dec_1(pp, sk_A, ct_A, proxy_cond, 32)
        end_time = time.clock()
        run_time += end_time - start_time
    print('cpre-dec_1: %s ms' % (((run_time)*1000)/RUN_TIMES)) 

    #ct_A =  cpre_sm9.enc(pp, pk_A, msg, proxy_cond, 32)
    # user A run cpre-rkeygen to get rkey(A to B)
    run_time = 0
    for i in range(RUN_TIMES):
        start_time = time.clock()
        rk_A2B, m = cpre_sm9.rkeygen(proxy_cond, sk_A, pk_B)
        end_time = time.clock()
        run_time += end_time - start_time
    print('cpre-rkeygen: %s ms' % (((run_time)*1000)/RUN_TIMES)) 

    #rk_A2B, m = cpre_sm9.rkeygen(proxy_cond, sk_A, pk_B) 

# no threshold

    # user A run cpre-reenc to convert A's cipher to B's
    run_time = 0
    for i in range(RUN_TIMES):
        start_time = time.clock()
        cp_ct_reenc = cpre_sm9.reenc(rk_A2B, ct_A)
        end_time = time.clock()
        run_time += end_time - start_time
    print('cpre-reencrypt: %s ms' % (((run_time)*1000)/RUN_TIMES)) 
    
    # cp_ct_reenc = cpre_sm9.reenc(rk_A2B, ct_A)
    
    # user B run cpre-dec to decrypt the ciphertext
    run_time = 0
    for i in range(RUN_TIMES):
        start_time = time.clock()
        plain_text = cpre_sm9.dec_2(sk_B, cp_ct_reenc, proxy_cond, 32)
        end_time = time.clock()
        run_time += end_time - start_time
    print('cpre-dec2: %s ms' % (((run_time)*1000)/RUN_TIMES)) 

    # plain_text = cpre_sm9.dec(sk_B, cp_ct_reenc, proxy_cond, 32)
    print(plain_text)

# (t, n) Shamir Secret Share

    # user A share rkey(A to B) to agents
    # blind_secret, blind_key = cpre_sm9.blind_secret(m, pk_B)
    threshold = 41
    total_shares = 80
    agent_set = [ i for i in range(1,total_shares+1)]
    recon_set = random.sample(agent_set, threshold)

    run_time = 0
    for i in range(RUN_TIMES):
        start_time = time.clock()
        shares = cpre_sm9.shamir_share(m, threshold, total_shares, pk_B)
        end_time = time.clock()
        run_time += end_time - start_time
    print('(t,n)share: %s ms' % (((run_time)*1000)/RUN_TIMES)) 

    # shares = cpre_sm9.shamir_share(blind_secret, threshold, total_shares)

    # recon_shares = [share for share in shares if share[0] in recon_set]

    # agents run cpre-reenc to convert A's cipher to B's
    run_time = 0
    for i in range(RUN_TIMES):
        start_time = time.clock()
        partial_rk = cpre_sm9.shamir_recon(shares[0], recon_set)
        partial_ct = cpre_sm9.reenc(partial_rk, ct_A)
        end_time = time.clock()
        run_time += end_time - start_time
    print('(t,n) partial reenc: %s ms' % (((run_time)*1000)/RUN_TIMES)) 

    # blind_rk = cpre_sm9.shamir_recon(recon_shares, pk_B)
    # rk = cpre_sm9.unblind(blind_rk, blind_key)
    # cp_ct_reenc = cpre_sm9.reenc(rk, ct_A)
    # user B run cpre-dec to decrypt the ciphertext
    # plain_text_shamir = cpre_sm9.dec_2(sk_B, cp_ct_reenc, proxy_cond, 32)
    # print(plain_text_shamir)

# (n, n) Arithmetic Secret Share

    # user A share rkey(A to B) to agents
    secret = m
    total_shares = 5

    run_time = 0
    for i in range(RUN_TIMES):
        start_time = time.clock()
        rk_shares = cpre_sm9.arithmetic_share(secret, total_shares, pk_B)
        end_time = time.clock()
        run_time += end_time - start_time
    print('(n,n)share: %s ms' % (((run_time)*1000)/RUN_TIMES)) 
    
    # arith_shares, rk_shares = cpre_sm9.arithmetic_share(secret, total_shares, pk_B)

    # agents run cpre-reenc to convert A's cipher to B's

    partial_cts = []
    for rk_share in rk_shares:
        partial_ct = cpre_sm9.reenc(rk_share, ct_A)
        partial_cts.append(partial_ct)

    # user B aggregate the partial cipher from agents to get the complete cipher
    run_time = 0
    for i in range(RUN_TIMES):
        start_time = time.clock()
        res_ct = cpre_sm9.aggregate_ct(partial_cts)
        end_time = time.clock()
        run_time += end_time - start_time
    print('(n,n)aggregate: %s ms' % (((run_time)*1000)/RUN_TIMES)) 
    
    # res_ct = cpre_sm9.aggregate_ct(partial_cts)
    # print(res_ct)

    # user B run cpre-dec to decrypt the ciphertext
    plain_text_arith = cpre_sm9.dec_2(sk_B, res_ct, proxy_cond, 32)
    print(plain_text_arith)



