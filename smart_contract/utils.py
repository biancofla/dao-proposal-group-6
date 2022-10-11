from algosdk import (
    account,
    mnemonic
)

def generate_algorand_keypair():
    private_key, address = account.generate_account()
    passphrase = mnemonic.from_private_key(private_key)

    print(f"My address: {address}")
    print(f"My private key: {private_key}")
    print(f"My passphrase: {passphrase}")

if __name__ == "__main__":
    generate_algorand_keypair()