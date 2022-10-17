from algosdk.future import transaction
from algosdk.v2client import algod
from algosdk import (
    account,
    error,
    mnemonic
)

from pyteal import *

import datetime
import hashlib
import random
import base64
import time

algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token   = "WaAZx2zEW697U4maXB6LT9qK3WEIBh8rjgD7uxc0"

algod_client = algod.AlgodClient(
    algod_token, 
    algod_address, 
    {
        "X-API-Key": algod_token
    }
)

def deploy_contract(passphrase):
    """
        Deploy the smart contract.

        Args:
            passphrase (str): account passphrase.

        Returns:
            int: if successful, return the application index of 
            the deployed smart contract; otherwise, return -1.
    """
    with open("vote_approval.teal", "r") as f:
        approval = f.read()

    with open("vote_clear_state.teal", "r") as f:
        clear = f.read()

    private_key = mnemonic.to_private_key(passphrase)
    sender      = account.address_from_private_key(private_key)
    
    try:
        approval_result  = algod_client.compile(approval) 
        approval_program = base64.b64decode(approval_result["result"])

        clear_result  = algod_client.compile(clear) 
        clear_program = base64.b64decode(clear_result["result"])

        local_schema  = transaction.StateSchema(num_uints=1 , num_byte_slices=1)
        global_schema = transaction.StateSchema(num_uints=20, num_byte_slices=6)

        sp = algod_client.suggested_params()

        registration_begin = datetime.datetime.now()
        registration_end   = registration_begin + datetime.timedelta(seconds=60)
        vote_begin         = registration_end + datetime.timedelta(seconds=1)
        vote_end           = vote_begin + datetime.timedelta(seconds=120)

        registration_begin = int(time.mktime(registration_begin.timetuple()))
        registration_end   = int(time.mktime(registration_end.timetuple()))
        vote_begin         = int(time.mktime(vote_begin.timetuple()))
        vote_end           = int(time.mktime(vote_end.timetuple()))

        p   = 59
        q   = 29
        gen = 3

        app_args = [
            registration_begin, 
            registration_end, 
            vote_begin, 
            vote_end,
            p,
            q,
            gen
        ]

        app_create_txn = transaction.ApplicationCreateTxn(
            sender=sender,
            sp=sp,
            on_complete=transaction.OnComplete.NoOpOC,
            approval_program=approval_program,
            clear_program=clear_program,
            global_schema=global_schema,
            local_schema=local_schema,
            app_args=app_args,
        )
        signed_app_create = app_create_txn.sign(private_key)
        txid = algod_client.send_transaction(signed_app_create)

        result = transaction.wait_for_confirmation(algod_client, txid, 2)
        app_id = result["application-index"]

        return app_id
    except error.AlgodHTTPError as e:
        print(e)
        return -1

def opt_in(passphrase, app_id):
    """
        Perform the opt-in operation.

        Args:
            passphrase (str): account passphrase.
            app_id (int): application index.

        Returns:
            int: if successful, return the confirmation round; 
            otherwise, return -1.
    """
    private_key = mnemonic.to_private_key(passphrase)
    sender      = account.address_from_private_key(private_key)

    global_state, result = get_global_state(app_id), {}
    whitelisted_args = [
        base64.b64encode(arg.encode()).decode() 
        for arg in ["p", "q", "gen"]
    ]
    for item in global_state:
        k, v = item["key"], item["value"]
        if k in whitelisted_args: 
            result[base64.b64decode(k).decode()] = v["uint"]

    g_x, x_chal, x_proof = _generate_round_1_proof(
        result["p"],
        result["q"],
        result["gen"],
        sender
    )
    
    app_args = [
        g_x,
        x_chal,
        x_proof
    ]

    try:
        sp = algod_client.suggested_params()
        app_optin_txn = transaction.ApplicationOptInTxn(
            sender=sender,
            sp=sp, 
            index=app_id,
            app_args=app_args
        )

        signed_app_optin_txn = app_optin_txn.sign(private_key)

        txid = algod_client.send_transaction(signed_app_optin_txn)
        result = transaction.wait_for_confirmation(algod_client, txid, 2)

        confirmation_round = result["confirmed-round"]

        return confirmation_round
    except error.AlgodHTTPError as e:
        print(e)
        return -1

def vote(passphrase, app_id):
    """
        Perform the voting operation.

        Args:
            passphrase (str): account passphrase.
            app_id (int): application index.

        Returns:
            int: if successful, return the confirmation round; 
            otherwise, return -1.
    """
    private_key = mnemonic.to_private_key(passphrase)
    sender      = account.address_from_private_key(private_key)

    try:
        sp = algod_client.suggested_params()

        global_state, global_state_result = get_global_state(app_id), {}
        whitelisted_args = [
            base64.b64encode(arg.to_bytes(8, "big")).decode()
            for arg in range(1, 6)
        ]
        whitelisted_args.append(base64.b64encode("p".encode()).decode())
        whitelisted_args.append(base64.b64encode("q".encode()).decode())
        whitelisted_args.append(base64.b64encode("gen".encode()).decode())

        for item in global_state:
            k, v = item["key"], item["value"]
            if k in whitelisted_args: 
                global_state_result[base64.b64decode(k).decode()] = v["uint"]


        local_state, local_state_result = get_local_state(sender, app_id), {}
        whitelisted_args = [
            base64.b64encode(arg.encode()).decode() 
            for arg in ["Index"]
        ]
        for item in local_state:
            k, v = item["key"], item["value"]
            if k in whitelisted_args: 
                local_state_result[base64.b64decode(k).decode()] = v["uint"]

        p   = global_state_result.pop("p")
        q   = global_state_result.pop("q")
        gen = global_state_result.pop("gen")

        print(local_state_result)

        index, g_x, voting_key, x_vote, a_1, b_1, a_2, b_2, d_1, r_1, d_2, r_2, hash = _generate_round_2_proof(
            global_state_result,
            local_state_result["Index"],
            p,
            q,
            gen,
            sender
        )

        app_args = [
            "vote".encode(),
            index,
            g_x,
            voting_key,
            x_vote,
            a_1,
            b_1,
            a_2,
            b_2,
            d_1,
            r_1,
            d_2,
            r_2,
            hash
        ]

        sp.flat_fee = True
        sp.fee      = 5000
        app_call_no_op_txn = transaction.ApplicationNoOpTxn(
            sender=sender,
            sp=sp, 
            index=app_id,
            app_args=app_args
        )

        signed_app_call_no_op_txn = app_call_no_op_txn.sign(private_key)

        txid = algod_client.send_transaction(signed_app_call_no_op_txn)
        result = transaction.wait_for_confirmation(algod_client, txid, 2)

        confirmation_round = result['confirmed-round']

        return confirmation_round
    except error.AlgodHTTPError as e:
        print(e)
        return -1

def get_global_state(app_id):
    """
        Get application's global state.

        Args:
            app_id (int): application index.

        Returns:
            (dict): application's global state.
    """
    global_state = {}
    try:
        app_info = algod_client.application_info(app_id)

        global_state = app_info["params"]["global-state"]
    except error.AlgodHTTPError as e:
        print(e)
    finally:
        return global_state

def get_local_state(address, app_id):
    """
        Get application's local state.

        Args:
            address (str): account's address.
            app_id (int): application index.

        Returns:
            (dict): application's local state.
    """
    local_state = {}
    try:
        account_info = algod_client.account_info(address)
        for ls in account_info["apps-local-state"]:
            if ls["id"] == app_id:
                local_state = ls["key-value"]
                break
    except error.AlgodHTTPError as e:
        print(e)
    finally:
        return local_state

def get_voting_results(passphrase, app_id):
    """
        Retrieve the voting results.

        Args:
            app (int): application index.

        Returns:
            dict: if successful, return the voting results; 
            otherwise, return an empty dictionary.
    """
    private_key = mnemonic.to_private_key(passphrase)
    sender      = account.address_from_private_key(private_key)

    try:
        sp = algod_client.suggested_params()

        app_args = [
            "results".encode()
        ]

        app_call_no_op_txn = transaction.ApplicationNoOpTxn(
            sender=sender,
            sp=sp, 
            index=app_id,
            app_args=app_args
        )

        signed_app_call_no_op_txn = app_call_no_op_txn.sign(private_key)

        txid = algod_client.send_transaction(signed_app_call_no_op_txn)
        result = transaction.wait_for_confirmation(algod_client, txid, 2)

        confirmation_round = result['confirmed-round']

        return confirmation_round
    except error.AlgodHTTPError as e:
        print(e)
        return -1
        
def _generate_round_1_proof(p, q, g, address):
    x = random.randint(1, q - 1)
    with open(f"{address}.txt", "w") as f:
        f.write(str(x))
    g_x = pow(g, x, p)

    rnd = random.randint(1, q - 1)
    g_rnd = pow(g, rnd, p)

    bytes_concat = (
        g.to_bytes(8, byteorder="big") 
        + g_x.to_bytes(8, byteorder="big")
        + g_rnd.to_bytes(8, byteorder="big")
    )
    digest = hashlib.sha256(bytes_concat).digest()
    x_chal = int.from_bytes(digest[:7], "big") % q

    x_proof = (rnd - x_chal * x) % q

    return g_x, g_rnd, x_proof

def _generate_round_2_proof(partecipants, index, p, q, gen, address):
    with open(f"{address}.txt", "r") as f:
        x = int(f.read())
    g_x = pow(gen, x, p)

    voting_key = _get_voting_key(partecipants, index, p, x)

    vote = random.randint(0, 1)
    print(f"Address: {address}; Vote: {vote}")
    if vote == 1:
        x_vote = (pow(voting_key, x, p) * gen) % p
        w_rnd, r_rnd, d_rnd = \
            random.randint(1, q - 1), random.randint(1, q - 1), random.randint(1, q - 1)
        a_1 = (pow(gen, r_rnd, p) * pow(g_x, d_rnd, p)) % p
        b_1 = (pow(voting_key, r_rnd, p) * pow(x_vote, d_rnd, p)) % p
        a_2 = pow(gen, w_rnd, p) % p
        b_2 = pow(voting_key, w_rnd, p) % p

        bytes_concat = (
            index.to_bytes(8, byteorder="big") 
            + g_x.to_bytes(8, byteorder="big")
            + voting_key.to_bytes(8, byteorder="big")
            + x_vote.to_bytes(8, byteorder="big")
            + a_1.to_bytes(8, byteorder="big")
            + b_1.to_bytes(8, byteorder="big")
            + a_2.to_bytes(8, byteorder="big")
            + b_2.to_bytes(8, byteorder="big")
        )
        digest = hashlib.sha256(bytes_concat).digest()
        x_chal_vote = int.from_bytes(digest[:7], "big") % q

        d_2 = (x_chal_vote - d_rnd) % q
        r_2 = (w_rnd - (x * d_2)) % q

        return index, g_x, voting_key, x_vote, a_1, b_1, a_2, b_2, d_rnd, r_rnd, d_2, r_2, x_chal_vote
    else:
        x_vote = (pow(voting_key, x, p)) % p
        w_rnd, r_rnd, d_rnd = \
            random.randint(1, q - 1), random.randint(1, q - 1), random.randint(1, q - 1)
        a_1 = pow(gen, w_rnd, p) % p
        b_1 = pow(voting_key, w_rnd, p) % p
        a_2 = (pow(gen, r_rnd, p) * pow(g_x, d_rnd, p)) % p
        b_2 = (pow(voting_key, r_rnd, p) * pow((x_vote * pow(gen, -1 , p)), d_rnd, p)) % p

        bytes_concat = (
            index.to_bytes(8, byteorder="big") 
            + g_x.to_bytes(8, byteorder="big")
            + voting_key.to_bytes(8, byteorder="big")
            + x_vote.to_bytes(8, byteorder="big")
            + a_1.to_bytes(8, byteorder="big")
            + b_1.to_bytes(8, byteorder="big")
            + a_2.to_bytes(8, byteorder="big")
            + b_2.to_bytes(8, byteorder="big")
        )
        digest = hashlib.sha256(bytes_concat).digest()
        y_chal_vote = int.from_bytes(digest[:7], "big") % q

        d_2 = (y_chal_vote - d_rnd) % q
        r_2 = (w_rnd - (x * d_2)) % q

        return index, g_x, voting_key, x_vote, a_1, b_1, a_2, b_2, d_2, r_2, d_rnd, r_rnd, y_chal_vote

def _get_voting_key(partecipants, index, p, x):
    voting_key = 1
    for idx, g_x_idx in partecipants.items():
        idx = int.from_bytes(idx.encode(), "big")
        if idx < index:
            voting_key = (voting_key * g_x_idx) % p
        else:
            voting_key = (voting_key * pow(index, -1, p)) % p
    return pow(voting_key, x, p)

def test():
    creator_passphrase = "between marine insane trash crane kick average spot twin pumpkin toast before setup top tomato inmate frozen picnic wall pilot glass claim camera about prosper"

    # Be sure that these accounts have some Algos.
    partecipant_passphrases = [
        "century hello diary ankle wire egg want flight fantasy good power now tiger coast utility chuckle two slot income wisdom nothing train flag abstract shaft",
        "annual include minute soup venue tornado panic mercy lemon jazz spring wise tide fitness slush six panther vibrant ancient today pole about lucky absent pond",
        "drama few keep ride exist mix spatial destroy agree swap coyote regret clay embrace review pencil recipe dust fossil myself change trade execute absorb junk",
        "purchase diary hamster harvest ignore whip minor retire search bird picnic suit almost fever history uncover since tobacco accuse team vehicle patrol twenty ability small",
        "buzz wrist whisper total robot hundred rain output crucial tone record arrive alert elder crisp neglect infant sport embrace doctor six tornado tunnel ability focus"
    ]

    creator_public_key      = mnemonic.to_public_key(creator_passphrase)
    partecipant_public_keys = [mnemonic.to_public_key(p) for p in partecipant_passphrases]

    print(f"# POLL CREATOR ADDRESS:\n{creator_public_key}")
    print("# PARTECIPANTS ADDRESSES:")
    for p in partecipant_public_keys: print(p)

    app_id = deploy_contract(creator_passphrase)
    print(app_id)
    if app_id > -1:
        print(f"Smart Contract succesfully created with App ID {app_id}.")

        # Opt-In all the partecipants.
        for passphrase, public_key in zip(partecipant_passphrases, partecipant_public_keys):
            res = opt_in(passphrase, app_id)

            if res > -1: 
                print(f"{public_key} opt-in performed succesfully.")
            else:
                print(f"Error in {public_key} opt-in.")
        
        # Wait for voting to start.
        print("Waiting for voting to start. It may take a while...")
        time.sleep(80)

        # Cast partecipants votes.
        for passphrase, public_key in zip(partecipant_passphrases, partecipant_public_keys):
            res = vote(passphrase, app_id)
            if res > -1: 
                print(f"{public_key} vote performed succesfully.")
            else:
                print(f"Error in {public_key} vote.")

        time.sleep(140)
                
        get_voting_results(partecipant_passphrases[0], app_id)

if __name__ == "__main__":
    test()
