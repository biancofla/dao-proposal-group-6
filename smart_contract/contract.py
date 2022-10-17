from pyteal import *

def approval_program():
    on_creation = Seq([
        App.globalPut(Bytes("Creator"), Txn.sender()),
        Assert(Txn.application_args.length() == Int(7)),
        App.globalPut(Bytes("RegBegin"), Btoi(Txn.application_args[0])),
        App.globalPut(Bytes("RegEnd"), Btoi(Txn.application_args[1])),
        App.globalPut(Bytes("VoteBegin"), Btoi(Txn.application_args[2])),
        App.globalPut(Bytes("VoteEnd"), Btoi(Txn.application_args[3])),
        App.globalPut(Bytes("p"), Btoi(Txn.application_args[4])),
        App.globalPut(Bytes("q"), Btoi(Txn.application_args[5])),
        App.globalPut(Bytes("gen"), Btoi(Txn.application_args[6])),
        App.globalPut(Bytes("CurrentIndex"), Int(0)),
        Return(Int(1))
    ])

    is_creator = Txn.sender() == App.globalGet(Bytes("Creator"))

    get_vote_of_sender = App.localGetEx(Int(0), App.id(), Bytes("voted"))

    on_show_results = Seq([
        Assert(
            Global.latest_timestamp() >= App.globalGet(Bytes("VoteEnd"))
        ),
        count_votes(),
        Return(Int(1))
    ])

    on_register = Seq([
        Assert(
            And(
                Global.latest_timestamp() >= App.globalGet(Bytes("RegBegin")),
                Global.latest_timestamp() <= App.globalGet(Bytes("RegEnd")),
                verify_r1(
                    Btoi(Txn.application_args[0]), 
                    Btoi(Txn.application_args[1]), 
                    Btoi(Txn.application_args[2])
                )
            )
        ),
        App.globalPut(
            Bytes("CurrentIndex"), 
            App.globalGet(Bytes("CurrentIndex")) + Int(1)
        ),
        App.globalPut(
            Itob(App.globalGet(Bytes("CurrentIndex"))), 
            Btoi(Txn.application_args[0])
        ),
        App.localPut(
            Txn.sender(),
            Bytes("Index"),
            App.globalGet(Bytes("CurrentIndex"))
        ),
        Return(Int(1))
    ])

    opup = OpUp(OpUpMode.OnCall)
    on_vote = Seq([
        opup.maximize_budget(Int(3000)),
        Assert(
            And(
                Global.latest_timestamp() >= App.globalGet(Bytes("VoteBegin")),
                Global.latest_timestamp() <= App.globalGet(Bytes("VoteEnd")),
                verify_r2(
                    Btoi(Txn.application_args[1] ), 
                    Btoi(Txn.application_args[2] ), 
                    Btoi(Txn.application_args[3] ),
                    Btoi(Txn.application_args[4] ),
                    Btoi(Txn.application_args[5] ),
                    Btoi(Txn.application_args[6] ),
                    Btoi(Txn.application_args[7] ),
                    Btoi(Txn.application_args[8] ), 
                    Btoi(Txn.application_args[9] ), 
                    Btoi(Txn.application_args[10]),
                    Btoi(Txn.application_args[11]),
                    Btoi(Txn.application_args[12]),
                    Btoi(Txn.application_args[13])
                )
            )
        ),
        App.globalPut(
            Concat(Bytes("Vote_"), Txn.application_args[1]),
            Btoi(Txn.application_args[5])
        ),
        #get_vote_of_sender,
        #If(get_vote_of_sender.hasValue(), Return(Int(0))),
        #App.globalPut(choice, choice_tally + Int(1)),
        #App.localPut(Int(0), Bytes("voted"), choice),
        Return(Int(1))
    ])

    program = Seq([
        Cond(
            [Txn.application_id() == Int(0), on_creation],
            [Txn.on_completion() == OnComplete.DeleteApplication, Return(is_creator)],
            [Txn.on_completion() == OnComplete.UpdateApplication, Return(is_creator)],
            [Txn.on_completion() == OnComplete.OptIn, on_register],
            [Txn.application_args[0] == Bytes("vote"), on_vote],
            [Txn.application_args[0] == Bytes("results"), on_show_results],
        )
    ])

    return program

def clear_state_program():
    get_vote_of_sender = App.localGetEx(Int(0), App.id(), Bytes("voted"))
    program = Seq([
        get_vote_of_sender,
        If(
            And(
                Global.latest_timestamp() <= App.globalGet(Bytes("VoteEnd")), 
                get_vote_of_sender.hasValue()
            ),
            App.globalPut(
                get_vote_of_sender.value(), 
                App.globalGet(get_vote_of_sender.value()) - Int(1)
            ),
        ),
        Return(Int(1))
    ])

    return program

@Subroutine(TealType.uint64)
def add_mod(a, b, mod):
    b_ = ScratchVar(TealType.uint64)
    
    return If(
        Eq(b, Int(0))
    ).Then(
        Return(a)
    ).Else(
        Seq([
            b_.store(mod - b),
            If(
                Ge(a, b_.load())
            ).Then(
                Return(a - b_.load())
            ).Else(
                Return(mod - b_.load() + a)
            )
        ])
    )

@Subroutine(TealType.uint64)
def mult_mod(a, b, mod):
    a_  = ScratchVar(TealType.uint64)
    b_  = ScratchVar(TealType.uint64)
    res = ScratchVar(TealType.uint64)

    return Seq([
        a_.store(a),
        b_.store(b),
        res.store(Int(0)),
        While(
           Gt(b_.load(), Int(0))
        ).Do(
            If(
               Eq(b_.load() % Int(2), Int(1))
            ).Then(
               res.store(add_mod(res.load(), a_.load(), mod))
            ),
            a_.store(add_mod(a_.load(), a_.load(), mod)),
            b_.store(Div(b_.load(), Int(2)))
        ),
        Return(res.load())
    ])

@Subroutine(TealType.uint64)
def pow_mod(base, exp, mod):
    base_ = ScratchVar(TealType.uint64)
    exp_  = ScratchVar(TealType.uint64)
    res   = ScratchVar(TealType.uint64)

    return Seq([
        base_.store(base),
        exp_.store(exp),
        res.store(Int(1)),
        While(
            Gt(exp_.load(), Int(0))
        ).Do(
            If(
               Eq(exp_.load() % Int(2), Int(1))
            ).Then(
               #res.store(mult_mod(res.load(), base_.load(), mod))
               res.store((res.load() * base_.load()) % mod)
            ),
            #base_.store(mult_mod(base_.load(), base_.load(), mod)),
            base_.store((base_.load() * base_.load()) % mod),
            exp_.store(Div(exp_.load(), Int(2)))
        ),
        Return(res.load())
    ])

@Subroutine(TealType.uint64)
def inverse_mod(b, mod):
    a         = ScratchVar(TealType.uint64)
    b_        = ScratchVar(TealType.uint64)
    t_1       = ScratchVar(TealType.uint64)
    t_2       = ScratchVar(TealType.uint64)
    t_1_sign  = ScratchVar(TealType.uint64)
    t_2_sign  = ScratchVar(TealType.uint64)
    quotient  = ScratchVar(TealType.uint64)
    remainder = ScratchVar(TealType.uint64)
    tmp_var   = ScratchVar(TealType.uint64)
    tmp_sign  = ScratchVar(TealType.uint64)

    return Seq([
        a.store(mod),
        b_.store(b),
        t_1.store(Int(0)),
        t_2.store(Int(1)),
        t_1_sign.store(Int(1)),
        t_2_sign.store(Int(1)),
        While(
            Neq(b_.load(), Int(0))
        ).Do(
            quotient.store(Div(a.load(), b_.load())),
            remainder.store(a.load() % b_.load()),
            a.store(b_.load()),
            b_.store(remainder.load()),
            tmp_var.store(t_2.load()),
            tmp_sign.store(t_2_sign.load()),
            If(
                Eq(t_1_sign.load(), t_2_sign.load())
            ).Then(
                If(
                    Ge(t_1.load(), quotient.load() * t_2.load())
                ).Then(
                    t_2.store(t_1.load() - quotient.load() * t_2.load())
                ).Else(
                    Seq([
                        t_2.store(quotient.load() * t_2.load() - t_1.load()),
                        t_2_sign.store(BitwiseXor(t_2_sign.load(), Int(1)))
                    ])
                    
                )
            ).Else(
                Seq([
                    t_2.store(t_1.load() + quotient.load() * t_2.load()),
                    t_2_sign.store(BitwiseXor(t_2_sign.load(), Int(1)))
                ])
            ),
            t_1.store(tmp_var.load()),
            t_1_sign.store(tmp_sign.load())
        ),
        If(
            Eq(t_1_sign.load(), Int(0))
        ).Then(
            Return(mod - t_1.load())
        ).Else(
            Return(t_1.load())
        )
    ])

@Subroutine(TealType.uint64)
def verify_r1(claim_id, claim_rnd, proof):
    chal = ScratchVar(TealType.uint64)

    p   = App.globalGet(Bytes("p"))
    q   = App.globalGet(Bytes("q"))
    gen = App.globalGet(Bytes("gen"))

    return Seq([
        chal.store(
            Btoi(Substring(Sha256(Concat(Itob(gen), Itob(claim_id), Itob(claim_rnd))), Int(0), Int(7))) % q
        ),
        If(
            Eq(
                #mult_mod(pow_mod(gen, proof, p), pow_mod(claim_id, chal.load(), p), p),
                (pow_mod(gen, proof, p) * pow_mod(claim_id, chal.load(), p)) % p,
                claim_rnd
            )
        ).Then(
            Return(Int(1))
        ).Else(
            Return(Int(0))
        )
    ])

@Subroutine(TealType.uint64)
def verify_r2(index, commit, key, vote, a_1, b_1, a_2, b_2, d_1, r_1, d_2, r_2, hash):
    chal = ScratchVar(TealType.uint64)

    p   = App.globalGet(Bytes("p"))
    q   = App.globalGet(Bytes("q"))
    gen = App.globalGet(Bytes("gen"))

    return Seq([
        chal.store(
            Btoi(
                Substring(
                    Sha256(
                        Concat(
                            Itob(index), 
                            Itob(commit), 
                            Itob(key),
                            Itob(vote), 
                            Itob(a_1), 
                            Itob(b_1), 
                            Itob(a_2), 
                            Itob(b_2)
                        )
                    ), 
                    Int(0), 
                    Int(7)
                )
            ) % q
        ),
        If(
            And(
                Eq(
                    chal.load(), 
                    (d_1 + d_2) % q
                ),
                Eq(
                    a_1,
                    (pow_mod(gen, r_1, p) * pow_mod(commit, d_1, p)) % p
                ),
                Eq(
                    a_2,
                    (pow_mod(gen, r_2, p) * pow_mod(commit, d_2, p)) % p
                ),
                Eq(
                    b_1,
                    (pow_mod(key, r_1, p) * pow_mod(vote, d_1, p)) % p
                ),
                Eq(
                    b_2,
                    (pow_mod(key, r_2, p) * pow_mod((vote * inverse_mod(gen, p)) % p, d_2, p)) % p
                ),
            )
        ).Then(
            Return(Int(1))
        ).Else(
            Return(Int(0))
        )
    ])

@Subroutine(TealType.none)
def count_votes():
    tot      = ScratchVar(TealType.uint64)
    votes    = ScratchVar(TealType.uint64)
    test_tot = ScratchVar(TealType.uint64)

    p   = App.globalGet(Bytes("p"))
    gen = App.globalGet(Bytes("gen"))

    current_index = App.globalGet(Bytes("CurrentIndex"))
    
    i = ScratchVar(TealType.uint64)
    j = ScratchVar(TealType.uint64)
    return Seq([
        tot.store(Int(1)),
        For(
            i.store(Int(0)),
            Lt(i.load(), current_index),
            i.store(i.load() + Int(1))
        ).Do(
            votes.store(
                App.globalGet(
                    Concat(Bytes("Vote_"), Itob(i.load()))
                )
            ),
            tot.store(
                (tot.load() * votes.load()) % p
            )
        ),
        test_tot.store(Int(1)),
        If(
            Eq(test_tot.load(), tot.load())
        ).Then(
            Seq([
                App.globalPut(
                    Bytes("Results"),
                    tot.load()
                ),
                #Return(Int(1))
            ])
        ).Else(
            For(
                j.store(Int(0)),
                Lt(j.load(), current_index),
                j.store(j.load() + Int(1))
            ).Do(
                test_tot.store(
                    (test_tot.load() * gen) % p
                ),
                If(
                    Eq(test_tot.load(), tot.load())
                ).Then(
                    Seq([
                        App.globalPut(
                            Bytes("Results"),
                            j.load() + Int(1)
                        ),
                        #Return(Int(1))
                    ]) 
                )
            )
        ),
        #Return(Int(0))
    ])

if __name__ == "__main__":
    with open('vote_approval.teal', 'w') as f:
        compiled = compileTeal(
            approval_program(), 
            Mode.Application,
            version=6
        )
        f.write(compiled)

    with open('vote_clear_state.teal', 'w') as f:
        compiled = compileTeal(
            clear_state_program(), 
            Mode.Application,
            version=6
        )
        f.write(compiled)
