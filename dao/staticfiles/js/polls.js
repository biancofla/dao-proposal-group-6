function redirectToCreatePoll() {
    window.location.replace("/new");
}

function onCreatePoll() {
    console.log("Create Poll");
}

function redirectToVotingPage(item) {
    window.location.replace(`/vote?app_id=${"whatever"}`);
}

function onOptIn() {
    console.log("opt-in");
}

function onVote() {
    console.log("vote");
}

function redirectToResultsPage(item) {
    window.location.replace(`/results?app_id=${"whatever"}`);
}