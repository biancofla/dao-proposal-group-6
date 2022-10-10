# Group 6 - Flavio Biancospino, Riccardo Marchesin, Nicolò Moriconi

Blockchains are naturally suited to implement decentralized voting systems. However, given the public nature of the blockchain, it is not easy to ensure the anonymity of voting and voters. We want to address these problems by implementing the Open Vote Network protocol.

The project's objective is to create a DAO with a limited number of participants that allows the creation of surveys and voting operations. Voting operations should be two-rounded and encrypted through the Open Vote Network protocol.

## State of the art

OVN is a self tallying voting protocol which has been first described in [Anonimous voting by two-round public discussion](http://homepages.cs.ncl.ac.uk/feng.hao/files/OpenVote_IET.pdf). While there exist implementations of it over the Ethereum blockchain (see for example [here](https://github.com/stonecoldpat/anonymousvoting)), to the best of our knowledge there is no implementation of the protocol in Algorand.

## Technical challenges

The technical challenges we expect to face concerning developing an e-voting DAPP on Algorand with the anonymity feature of the voters and the votes, that allows users to create polls and vote. As far as we know, this hasn't been released in these few days of searching through the web.
There are several examples of this kind of implementation on other blockchains, like Ethereum, and we are trying to replicate the Open Vote protocol on the Algorand blockchain. Implementing the Open Vote Network protocol, we expect to encounter significant technical challenges in implementing non-interactive ZKPs.
In this way, we can take advantage of some pros that Algorand has: faster, cheaper, and more energy efficient.

# Demo

An interactive demo of the application is deployed at the following [link](https://dao-proposal-group-6.fly.dev/).
