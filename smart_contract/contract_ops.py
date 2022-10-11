from algosdk.future import transaction
from algosdk.v2client import algod
from algosdk import (
    account,
    error,
    mnemonic
)

from pyteal import *

import datetime
import random
import base64
import time

algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token   = "<PURESTAKE_API_TOKEN>"

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

        local_schema  = transaction.StateSchema(num_uints=0, num_byte_slices=1)
        global_schema = transaction.StateSchema(num_uints=6, num_byte_slices=1)

        sp = algod_client.suggested_params()

        registration_begin = datetime.datetime.now()
        registration_end   = registration_begin + datetime.timedelta(seconds=60)
        vote_begin         = registration_end + datetime.timedelta(seconds=1)
        vote_end           = vote_begin + datetime.timedelta(days=1)

        registration_begin = int(time.mktime(registration_begin.timetuple()))
        registration_end   = int(time.mktime(registration_end.timetuple()))
        vote_begin         = int(time.mktime(vote_begin.timetuple()))
        vote_end           = int(time.mktime(vote_end.timetuple()))

        app_args = [
            registration_begin, 
            registration_end, 
            vote_begin, 
            vote_end, 
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
            app (int): application index.

        Returns:
            int: if successful, return the confirmation round; 
            otherwise, return -1.
    """
    private_key = mnemonic.to_private_key(passphrase)
    sender      = account.address_from_private_key(private_key)

    try:
        sp = algod_client.suggested_params()
        app_optin_txn = transaction.ApplicationOptInTxn(
            sender=sender,
            sp=sp, 
            index=app_id
        )

        signed_app_optin_txn = app_optin_txn.sign(private_key)

        txid = algod_client.send_transaction(signed_app_optin_txn)
        result = transaction.wait_for_confirmation(algod_client, txid, 2)

        confirmation_round = result["confirmed-round"]

        return confirmation_round
    except error.AlgodHTTPError as e:
        print(e)
        return -1

def vote(passphrase, app_id, preference):
    """
        Perform the voting operation.

        Args:
            passphrase (str): account passphrase.
            app (int): application index.
            preference (int): account voting preference.

        Returns:
            int: if successful, return the confirmation round; 
            otherwise, return -1.
    """
    private_key = mnemonic.to_private_key(passphrase)
    sender      = account.address_from_private_key(private_key)

    try:
        sp = algod_client.suggested_params()

        app_args = [
            "vote".encode(),
            preference
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

def get_voting_results(app_id):
    """
        Retrieve the voting results.

        Args:
            app (int): application index.

        Returns:
            dict: if successful, return the voting results; 
            otherwise, return an empty dictionary.
    """
    args = [
        "RegBegin",
        "RegEnd",
        "VoteBegin",
        "VoteEnd",
        "Creator"
    ]
    args = [
        base64.b64encode(a.encode()).decode() 
        for a in args
    ]

    results = {}

    try:
        app_info = algod_client.application_info(app_id)

        global_state = app_info["params"]["global-state"]
        
        for item in global_state:
            k, v = item["key"], item["value"]
            if k not in args: 
                decoded_k = int.from_bytes(
                    base64.b64decode(k), 
                    "big"
                )
                results[str(decoded_k)] = v["uint"]
    except error.AlgodHTTPError as e:
        print(e)
    finally:
        return results

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
        time.sleep(120)

        # Cast partecipants votes.
        for passphrase, public_key in zip(partecipant_passphrases, partecipant_public_keys):
            res = vote(passphrase, app_id, random.randint(0, 1))
            if res > -1: 
                print(f"{public_key} vote performed succesfully.")
            else:
                print(f"Error in {public_key} vote.")
                
        results = get_voting_results(app_id)
        print(results)

if __name__ == "__main__":
    test()
