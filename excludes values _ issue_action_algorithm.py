## This entire function assumes that this will only be calculated once

def calculate_total_score(
    user_rankings: dict,
    org_rankings: dict,
    issue_categories: dict,
    user_actions: list,
    org_actions: list,
    weights: dict = {
        'exact_match': 0.7,
        'category_match': 0.3,
        'issue_weight': 0.7,
        'action_weight': 0.3
    }
) -> dict:
    """
    Calculate combined issue and action scores between user and organization
    
    Parameters:
    -----------
    user_rankings : dict
        Dictionary of user's issue rankings
    org_rankings : dict
        Dictionary of organization's issue rankings
    issue_categories : dict
        Dictionary mapping issues to their categories
    user_actions : list
        List of user's preferred actions
    org_actions : list
        List of organization's actions
    weights : dict, optional
        Dictionary of weights for different score components
        
    Returns:
    --------
    dict
        Dictionary containing issue_score, action_score, and total_score
    """
    
    # Calculate a few key elements you will use later
    user_max_rank = len(user_rankings)
    org_max_rank = len(org_rankings)
    scale_factor = user_max_rank / org_max_rank
    scaled_org_rankings = {
        issue: issue_rank * scale_factor 
        for issue, issue_rank in org_rankings.items()
    }
    
    # assign total_distance outside of the loops.
    # this will be incremented later to keep track of scores for each comparison
    total_distance = 0

    # assign the category_to_issues dictionary outside of the loops.
    # this dictionary will be filled with the issues and categories reversed
    category_to_issues = {}
    
    # This takes the issue keys and category values we define outside the function and unpacks them.
    # This takes the issue_categories and turns then into a new dictionary that looks like
    # {category: [issue1, issue2, issue3]}
    # // THIS WILL NOT BE EFFICIENT IF DONE EVERY TIME.
    # // THIS LOOP WILL NEED TO BE PRE-CALCULATED OUTSIDE OF THE FUNCTION.
    for issue, category in issue_categories.items():
        if category not in category_to_issues:
            category_to_issues[category] = []
        category_to_issues[category].append(issue)

# _______________________________________________________________________
    # ISSUE AND CATEGORY CALCULATIONS
    # This takes the scaled_org_rankings (which is the scaled version
    # of the original org_rankings dictionary) and only pulls out the key--> org_issues
    # "org_issue" represents a temporary variable representing the key in the dictionary
    for org_issue in scaled_org_rankings:

        # This assigns the value of the org_issue key from the "issue_categories" dictionary
        # to the variable org_issue_rank
        org_category = issue_categories.get(org_issue)

        # We will increment "exact_distance" so we give it a zero value to start
        exact_distance = 0
        
        # This searches for the "org_issue" 
        # that we pulled earlier from the "scaled_org_rankings" dictionary
        # and checks if the issue key appears in "user_rankings"
        if org_issue in user_rankings:

            # If the "org_issue" key is also in the "user_rankings" dictionary
            # Calculate the "exact_distance" by subtracting the rank value of
            # "org_issue" key in the "scaled_org_rankings" dictionary from the rank value of
            # "org_issue" key in the "user_rankings" dictionary 
            exact_distance = abs(user_rankings[org_issue] - scaled_org_rankings[org_issue])
        else:

            # In the event that the "org_issue" key isn't in the "user_rankings"
            # "exact_distance" will be give the user_max_rank calculated outside the loop.
            exact_distance = user_max_rank

        # Now we move onto category distances   
        category_distance = user_max_rank
        
        # If there is an "org_issue_rank" that can be called
        if org_category:

            # Assign the worst possible distance to the "best_category_distance" variable
            # We will check in the for-loop for a better distance, 
            # but will use "user_max_rank" if needed.
            best_category_distance = user_max_rank

            # Initialize a loop looking for each key in the "user_rankings" dictionary
            # "user_issue" represents a temporary variable representing the key in the dictionary
            for user_issue in user_rankings:
                
                # Using the issue key in the "issue_categories" dictionary,
                # Search for the "user_issue" key and it's associated category value
                # Then compare that category value to the category value found previously
                # and stored in "org_category"
                # If these values are identical, move forward
                if issue_categories.get(user_issue) == org_category:

                    # Once you have confirmed that the org_category and user_category are identical
                    # Use the "user_issue" to pull the value from "user_rankings" and
                    # Use the "org_issue" to pull the value from "scaled_org_ranks" and
                    # Subtract the "org_issue" from the "user_issue"
                    # And save the absolute value of that calculation to "current_distance"
                    current_distance = abs(user_rankings[user_issue] - scaled_org_rankings[org_issue])

                    # Find the minimum value between the "current_distance" and "best_category_distance"
                    # Reassign the smallest of the two values into "best_category_distance"
                    best_category_distance = min(best_category_distance, current_distance)
            
            # Loop until the "user_issue" key returns no further values from "issue_categories"
            # Assign the "best_category_distance" to a new variable called "category_distance"
            category_distance = best_category_distance
        
        # Take the "exact_distance" and "category_distance" values calculated before
        # And multiply them by their respective weights defined in the "weights" dictionary
        # Add both results together and assign the result to weighted_distance
        #This calls on the dictionary of weights to calculate weights.
        weighted_distance = (exact_distance * weights['exact_match'] + 
                           category_distance * weights['category_match'])
        
        # Repeat this process until all issues have been compared to one another
        total_distance += weighted_distance
    
    #This calls on the dictionary of weights to calculate weights.
    final_issue_score = (total_distance / user_max_rank) * weights['issue_weight']


# _______________________________________________________________________  
    # ACTION SCORE CALCULATION
    # Create a set from the list of "user_actions" and "org_actions"
    user_set = set(user_actions)
    org_set = set(org_actions)
    
    # If there is an intersection between the "user_set" and "org_set"
    if user_set and org_set:

        # Calculate the number of intersections by taking the length
        # of the list of intersected elements
        action_intersection = len(user_set & org_set)

        # Calculate the total length of both the "user_set" and "org_set"
        # by creating a list that includes values in "user_set" or "org_set"
        action_union = len(user_set | org_set)

        # Calculate the similarity of intersections by
        # dividing the number of intersections by the union of the two lists
        action_similarity = action_intersection / action_union

        # Calculate the "action_score" by subtracting the "action_similarity" 
        # from the number 1 and multiplying it by the length of the "user_set"
        action_score = (1 - action_similarity) * len(user_set)
    else:

        # If there are no intersections between the "user_set" and "org_set",
        # Assign the "action_score" the worst case scenario which is the 
        # Total number of elements in the "user_set"
        action_score = len(user_set)
    
    # Multiply the "action_score" by the weight 
    # defined in the "weight" dictionary and assign it to "final_action_score"
    final_action_score = action_score * weights['action_weight']

##_______________________________________________________________________
    # Calculate total score and round all scores
    return {
        'issue_score': round(final_issue_score, 2),
        'action_score': round(final_action_score, 2),
        'total_score': round(final_issue_score + final_action_score, 2)
    }

# Test the function with example data
if __name__ == "__main__":
    # Example data
    new_user = {
        "Gun Control": 1,
        "Mental Health": 2,
        "LGBTQ Rights": 3
    }

    new_org = {
        "Gun Violence Prevention": 1,
        "Depression Awareness": 2,
        "Marriage Equality": 3,
        "Gender Identity": 4
    }

    new_user_actions = ["volunteer", "donate", "social media"]
    new_org_actions = ["volunteer", "lobby", "campaign", "social media"]

    new_issue_categories = {
        "Gun Control": "Public Safety",
        "Gun Violence Prevention": "Public Safety",
        "Mental Health": "Healthcare",
        "Depression Awareness": "Healthcare",
        "LGBTQ Rights": "Civil Rights",
        "Marriage Equality": "Civil Rights",
        "Gender Identity": "Civil Rights"
    }

    # Calculate with default weights
    # Notice that the function is called within if __name__ == "__main__"
    # instead of outside of it.
    results = calculate_total_score(
        new_user,
        new_org,
        new_issue_categories,
        new_user_actions,
        new_org_actions
    )
    print("Results with default weights:", results)

    # Calculate with custom weights
    #THIS IS VERY INTERESTION BECAUSE WEIGHTS CAN BE CHANGED LATER
    custom_weights = {
        'exact_match': 0.8,
        'category_match': 0.2,
        'issue_weight': 0.6,
        'action_weight': 0.4
    }
    
    results_custom = calculate_total_score(
        new_user,
        new_org,
        new_issue_categories,
        new_user_actions,
        new_org_actions,
        custom_weights
    )
    print("\nResults with custom weights:", results_custom)