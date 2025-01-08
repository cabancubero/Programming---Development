function calculateTotalScore(
    userRankings, 
    orgRankings, 
    issueCategories, 
    userActions, 
    orgActions,
    weights = { 
        exactMatch: 0.7,
        categoryMatch: 0.3,
        issueWeight: 0.7,
        actionWeight: 0.3
    }
) {
    // Issue score calculation
    const userMaxRank = Object.keys(userRankings).length;
    const orgMaxRank = Object.keys(orgRankings).length;
    const scaleFactor = userMaxRank / orgMaxRank;
    
    const scaledOrgRankings = {};
    for (const [issue, rank] of Object.entries(orgRankings)) {
        scaledOrgRankings[issue] = rank * scaleFactor;
    }
    
    let totalDistance = 0;
    
    for (const orgIssue of Object.keys(orgRankings)) {
        const orgCategory = issueCategories[orgIssue];
        let exactDistance = userMaxRank;
        
        if (orgIssue in userRankings) {
            exactDistance = Math.abs(userRankings[orgIssue] - scaledOrgRankings[orgIssue]);
        }
        
        let categoryDistance = userMaxRank;
        if (orgCategory) {
            let bestCategoryDistance = userMaxRank;
            for (const userIssue of Object.keys(userRankings)) {
                if (issueCategories[userIssue] === orgCategory) {
                    const currentDistance = Math.abs(userRankings[userIssue] - scaledOrgRankings[orgIssue]);
                    bestCategoryDistance = Math.min(bestCategoryDistance, currentDistance);
                }
            }
            categoryDistance = bestCategoryDistance;
        }
        
        const weightedDistance = (exactDistance * weights.exactMatch + 
                                categoryDistance * weights.categoryMatch);
        totalDistance += weightedDistance;
    }
    
    const issueScore = (totalDistance / userMaxRank) * weights.issueWeight;

    // Action score calculation
    const userSet = new Set(userActions);
    const orgSet = new Set(orgActions);
    
    let actionScore;
    if (userSet.size && orgSet.size) {
        const intersection = new Set([...userSet].filter(x => orgSet.has(x)));
        const union = new Set([...userSet, ...orgSet]);
        const actionSimilarity = intersection.size / union.size;
        actionScore = (1 - actionSimilarity) * userSet.size;
    } else {
        actionScore = userSet.size;
    }
    
    const finalActionScore = actionScore * weights.actionWeight;

    // Calculate total and round all scores
    return {
        issueScore: Number(issueScore.toFixed(2)),
        actionScore: Number(finalActionScore.toFixed(2)),
        totalScore: Number((issueScore + finalActionScore).toFixed(2))
    };
}

// Test with our example data
const new_user = {
    "Gun Control": 1,
    "Mental Health": 2,
    "LGBTQ Rights": 3
};

const new_org = {
    "Gun Violence Prevention": 1,
    "Depression Awareness": 2,
    "Marriage Equality": 3,
    "Gender Identity": 4
};

const new_user_actions = ["volunteer", "donate", "social media"];
const new_org_actions = ["volunteer", "lobby", "campaign", "social media"];

const new_issue_categories = {
    "Gun Control": "Public Safety",
    "Gun Violence Prevention": "Public Safety",
    "Mental Health": "Healthcare",
    "Depression Awareness": "Healthcare",
    "LGBTQ Rights": "Civil Rights",
    "Marriage Equality": "Civil Rights",
    "Gender Identity": "Civil Rights"
};

// Calculate scores
const results = calculateTotalScore(
    new_user,
    new_org,
    new_issue_categories,
    new_user_actions,
    new_org_actions
);

console.log("Results:", results);

// Test with custom weights
const customWeights = {
    exactMatch: 0.8,
    categoryMatch: 0.2,
    issueWeight: 0.6,
    actionWeight: 0.4
};

const resultsWithCustomWeights = calculateTotalScore(
    new_user,
    new_org,
    new_issue_categories,
    new_user_actions,
    new_org_actions,
    customWeights
);

console.log("\nResults with custom weights:", resultsWithCustomWeights);
