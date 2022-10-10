# Group 6 - Flavio Biancospino, Riccardo Marchesin, Nicolò Moriconi

Blockchains are naturally suited to implement decentralized voting systems. However, given the public nature of the blockchain, it is not easy to ensure the anonymity of voting and voters. We want to address these problems by implementing the Open Vote Network protocol. 

The project's objective is to create a DAO with a limited number of participants that allows the creation of surveys and voting operations. Voting operations should be two-rounded and encrypted through the Open Vote Network protocol.

## State of the art
 OVN is a self tallying voting protocol which has been first described in [Anonimous voting by two-round public discussion](http://homepages.cs.ncl.ac.uk/feng.hao/files/OpenVote_IET.pdf). While there exist implementations of it over the Ethereum blockchain (see for example [here](https://github.com/stonecoldpat/anonymousvoting)), to the best of our knowledge there is no implementation of the protocol in Algorand. 
 
 ## Technical challenges
The technical challenge we will face is implementing a DApp that allows users to create polls and vote within them. Also, in implementing the Open Vote Network protocol, we expect to encounter significant technical challenges in implementing non-interactive ZKPs.

# Demo

An interactive demo of the application is deployed at the following [link](https://dao-proposal-group-6.fly.dev/).
