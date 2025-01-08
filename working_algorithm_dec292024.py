# Example mapping of specific issues to general categories
def calculate_issue_score(
    user_rankings: dict, 
    org_rankings: dict,
    issue_categories: dict,
    exact_match_weight: float = 0.7,  # Weight for exact issue matches
    category_match_weight: float = 0.3,  # Weight for category matches
    issue_weight: float = .7
    
) -> float:
    
    user_max_rank = len(user_rankings)
    org_max_rank = len(org_rankings)
    scale_factor = user_max_rank / org_max_rank
    scaled_org_rankings = {
        issue: rank * scale_factor 
        for issue, rank in org_rankings.items()
    }
    
    total_distance = 0
    
    # Create reverse mapping of categories to issues
    category_to_issues = {}
    #Unpack the issue_categories dictionary's issue and category key:value pairs
    for issue, category in issue_categories.items():
        #If the category is not in the empty dictionary initialized before,
        if category not in category_to_issues:
            #Created a dictionary where the category is the key
            #And the empty list is the value
            #Will look something like
            # category_to_issues = {"category":[]}
            category_to_issues[category] = []
        # For the category added to the dictionary, 
        # append the issue key to the list
        # Will look something like 
        # category_to_issues = {category: [issue-key, issue-key]

        #This essentially reverses the original dictionary,
        # mapping issues as keys to categories as values
        category_to_issues[category].append(issue)
    
    #Now we loop through the org_rankings dictionary we created,
    #which looks like org_rankings = {"issue": rank, "issue":rank}
    #For each org_issue (used as a key in the dictionary)
    # ?? I wonder if we can just use the scaled_org_rankings dictionary here instead ??
    for org_issue in scaled_org_rankings:
        # Pull out the value for the org_issue key and assigns it to the org_category variable
        # This would look something like
        # issue_categories.get(org_issue) reads the org_issue key
        # org_category = saves the issue_categories value for the org_issue key
        # Because we are reading through the rankings, this means that
        # org_category = "rank", not "category"
        # But what this does, is it let's us later compare the reversed dictionary
        # To the rank value the org gave the issue
        org_category = issue_categories.get(org_issue)
        
        # Calculate exact match distance
        #First assign exact_distance a zero. This is the best possible scenario
        exact_distance = 0

        # org_issues have been unpacked before.
        # Remember that org_issues is equal to the key in org_rankings
        # org_rankings looks like {issue:rank}
        # Therefore, we are comparing the key "issue" to the user dictionary user_rankings = {issue: rank}
        if org_issue in user_rankings:

            # We add the absolute value of the differences to the variable exact_distance,
            # which was initialized before
            #//
            # The way this calulation works is that it takes the user_rankings dictionary,
            # it uses the org_issue unpacked before from the org_rankings dictionary,
            # to extract the value from that org_issue key.
            # Previously, we created an updated dictionary for the org_rankings called
            # scaled_org_rankings that scaled the values for each issue key
            # according to the scale_factor calculated before.
            # Using the scaled_org_rankings dictionary, 
            # we also search for the org_issue from the the org_rankings dictionary we unpacked before
            # and we return the value from the scaled_org_rankings
            # We subtracted the value for the key in scaled_org_rankings from
            # the value for the key in user_rankings
            # and we find the absolute value (this is so we are measuring distance between ranks)
            # And we assign the result to exact_distance
            exact_distance = abs(user_rankings[org_issue] - scaled_org_rankings[org_issue])
        else:
            #If the org_issue is not in the user_rankings, assign "exact_distance"
            # the maximum rank number. 
            # If the
            exact_distance = user_max_rank
            
        # Calculate category match distance
        # Default to max distance
        category_distance = user_max_rank  

        # Open a test within the loop for org_category
        if org_category:
            # Find best matching issue in same category from user rankings
            #Assume that the best_category_distance is the user_max_rank (which is the worst scenario)
            best_category_distance = user_max_rank

            # Open a for loop that pulls the key "user_issue" from the user_rankings dictionary.
            for user_issue in user_rankings:

                # Using the issue_categories dictionary created at the start
                # Look for the user_issue from user_rankings in the issue_categories dictionary
                # And see if it is equal to the org_category, which was previously assigned a "rank" from the org_rankings dictionary
                if issue_categories.get(user_issue) == org_category:
                    # Assign the variable "curent_distance" the absolute value of the value of the 
                    # user_issue's rank from the user_rankings dictionary
                    # Minus the org_issue rank from the scaled_org_rankings dictionary
                   
                    current_distance = abs(user_rankings[user_issue] - scaled_org_rankings[org_issue])

                    # Compare the "best_category_distance from before to the current_distance
                    # Before, "best_category_distance" was assigned the worst possible scenario
                    # If the "current_distance" is less than the best_category_distance,
                    # Assign the "best_category_distance" the new value of the lesser of the two compared values

                    best_category_distance = min(best_category_distance, current_distance)
            # Once the loop has compared all possible current_distances,
            # Assign the "best_category_distance" to the variable "category_distance"
            # which before had also been given the worst possible scenario of user_max_rank
            category_distance = best_category_distance
            
        # Combine distances with weights
        # We return to the top of this for loop and we calculate several things
        # We first pull exact_distance calculated in its corresponding loop
        # Then we multiply that by a weight value we assign in the opening of the function
        # We then pull the category_dsitance calculated in its corresponding loop
        # And we multiply that by the weight calue we assign in the opening of the function
        # We do this for every exact_distance calculation and every category_distance calculation

        weighted_distance = (exact_distance * exact_match_weight + 
                           category_distance * category_match_weight)
        # We create a counter that adds the value of these calculations called "weighted_distance"
        # To the counter "total_distance"
        total_distance += weighted_distance
        
    final_issue_score = (total_distance / user_max_rank)*issue_weight

    return round(final_issue_score,2)

def calculate_action_score(user_actions, org_actions, action_weight=.3):
    user_set = set(user_actions)
    org_set = set(org_actions)
    
    if user_set and org_set:
        action_intersection = len(user_set & org_set)
        action_union = len(user_set | org_set)
        action_similarity = action_intersection / action_union
        action_score = (1 - action_similarity) * len(user_set)
    else:
        action_score = len(user_set)
    
    final_action_score = action_score * action_weight
    
    return round(final_action_score,2)

    #This entire loop will continue until there are no more org_issues to compare to user_issues
    # At either the exact issue level or the category level  
    
    

        

# Example usage
user = {
    "Environmental Racism": 1,
    "HIV Prevention": 2
}

org = {
    "Climate Change": 1,
    "Abortion Rights": 2
}

user_actions = ["protest", "educate", "advocate"]

org_actions = ["protest", "research", "policy"]

issue_categories = {
    "Environmental Racism": "Environmental",
    "Climate Change": "Environmental",
    "HIV Prevention": "Reproductive Health",
    "Abortion Rights": "Reproductive Health"
}



match_action_score = calculate_action_score(user_actions, org_actions)
print(match_action_score)

match_issue_score = calculate_issue_score(
    user_rankings=user,
    org_rankings=org,
    issue_categories=issue_categories
)
print(match_issue_score)

