# Group 6 - Flavio Biancospino, Riccardo Marchesin, Nicolò Moriconi

Blockchains are naturally suited to implement decentralized voting systems. However, given the public nature of the blockchain, it is not easy to ensure the anonymity of voting and voters. We want to address these problems by implementing the Open Vote Network protocol.

## State of The Art

The research carried out by McCorry et al. [1] discusses secure methods to conduct e-voting in various settings.

In a traditional voting context, a central authority is responsible for the proper conduct of the voting process. However, in this context, the authorities in charge of tallying operations might make mistakes, whether intentional or not.

Technological developments have enabled the creation of digital voting systems through dedicated hardware and software. However, even in this case, the possibility of votes being counterfeited by third-party entities is a serious problem.

The use of blockchain technology is a viable solution to the problem described. Blockchain technology promotes decentralization by eliminating the presence of central authorities. Cryptographic evidence replaces central authorities. Thus, in the hypothetical context of a vote, the probability of vote forgery becomes infeasible.

McCorry et al. proposed a decentralized voting system based on the Ethereum blockchain and the _Open Vote Network protocol_ (from now on, it will be referred to as _OVN_). OVN is a self-tallying voting protocol that was first described in [2] and implemented in [3].

## Technical Challenges

As discussed before, while there exist implementations of OVN over the Ethereum blockchain, to the best of our knowledge, there is no implementation of such a protocol in Algorand. The use of the Algorand blockchain could considerably improve the voting system proposed by McCorry et al. The costs per transaction would be much lower; overall, each voting process would involve negligible expense. In addition, the Algorand network has proven to be faster, more reliable, and more energy-efficient: an optimal platform for creating and managing online votes.

The technical challenges we expect to face concern the development of an e-voting _Dentralized Application_ (from now on, it will be referred to as _DApp_) on Algorand with the anonymity feature of the voters and the votes that allows users to create polls and cast votes within these polls. Implementing the Open Vote Network protocol, we expect to encounter significant technical challenges in implementing non-interactive ZKPs.

## References

1. [On Secure E-Voting over Blockchain](https://dl.acm.org/doi/pdf/10.1145/3461461)
2. [Anonimous Voting by Two-Round Public Discussion](http://homepages.cs.ncl.ac.uk/feng.hao/files/OpenVote_IET.pdf)
3. [Anonimous Voting by Two-Round Public Discussion - Repository](https://github.com/stonecoldpat/anonymousvoting)

## Demo

An interactive demo of the application is deployed at the following [link](https://dao-proposal-group-6.fly.dev/).
