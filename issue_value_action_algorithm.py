def calculate_total_score(
    user_rankings: dict,
    org_rankings: dict,
    issue_categories: dict,
    user_actions: list,
    org_actions: list,
    user_values: dict = {},  # New parameter for user value responses
    org_values: dict = {},   # New parameter for org value responses
    weights: dict = {
        'exact_match': 0.7, # Weight for inner-loop exact issue matching calculations (can be changed)
        'category_match': 0.3, # Weight for inner-loop categorical matching calculations (can be changed)
        'issue_weight': 0.6, # Weight for outer-loop issue weight in total score (can be changed)
        'action_weight': 0.2,  # Weight for outer-loop action weight in total score (can be changed)
        'value_weight': 0.2   # Weight for outer-loop value weight in total score (can be changed)
    }
) -> dict:
    """
    Calculate combined issue, action, and value scores between user and organization
    
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
    user_values : dict
        Dictionary of user's value responses, format:
        {issue: {'q1': score, 'q2': score}}
    org_values : dict
        Dictionary of organization's value responses
    weights : dict, optional
        Dictionary of weights for different score components
        
    Returns:
    --------
    dict
        Dictionary containing issue_score, action_score, value_score, and total_score
    """
##_______________________________________________________________ 
    # Original scaling calculations
    user_max_rank = len(user_rankings)
    org_max_rank = len(org_rankings)
    scale_factor = user_max_rank / org_max_rank
    scaled_org_rankings = {
        issue: issue_rank * scale_factor 
        for issue, issue_rank in org_rankings.items()
    }
    
    total_distance = 0
    category_to_issues = {}
    
    for issue, category in issue_categories.items():
        if category not in category_to_issues:
            category_to_issues[category] = []
        category_to_issues[category].append(issue)

##_______________________________________________________________
    # ISSUE AND CATEGORY CALCULATIONS (unchanged)
    for org_issue in scaled_org_rankings:
        org_category = issue_categories.get(org_issue)
        exact_distance = 0
        
        if org_issue in user_rankings:
            exact_distance = abs(user_rankings[org_issue] - scaled_org_rankings[org_issue])
        else:
            exact_distance = user_max_rank

        category_distance = user_max_rank
        
        if org_category:
            best_category_distance = user_max_rank
            for user_issue in user_rankings:
                if issue_categories.get(user_issue) == org_category:
                    current_distance = abs(user_rankings[user_issue] - scaled_org_rankings[org_issue])
                    best_category_distance = min(best_category_distance, current_distance)
            category_distance = best_category_distance
        
        weighted_distance = (exact_distance * weights['exact_match'] + 
                           category_distance * weights['category_match'])
        total_distance += weighted_distance
    
    final_issue_score = (total_distance / user_max_rank) * weights['issue_weight']

##_______________________________________________________________
    # ACTION SCORE CALCULATION
    user_set = set(user_actions)
    org_set = set(org_actions)
    
    if user_set and org_set:
        action_intersection = len(user_set & org_set)
        action_union = len(user_set | org_set)
        action_similarity = action_intersection / action_union
        action_score = (1 - action_similarity) * len(user_set)
    else:
        action_score = len(user_set)
    
    final_action_score = action_score * weights['action_weight']

##_______________________________________________________________
    # VALUE QUESTIONS SCORE CALCULATION
    total_value_distance = 0
    num_value_questions = 0  # Track number of questions answered
    
    # Compare values for each issue that appears in both rankings
    for org_issue in org_rankings:
        if org_issue in user_rankings:
            org_issue_values = org_values.get(org_issue, {})
            user_issue_values = user_values.get(org_issue, {})
            
            # Compare each question's values
            for q in ['q1', 'q2']:
                org_value = org_issue_values.get(q)
                user_value = user_issue_values.get(q)
                
                # Only calculate if both org and user provided values for this question
                if org_value is not None and user_value is not None:
                    value_distance = abs(user_value - org_value)
                    total_value_distance += value_distance
                    num_value_questions += 1

##_______________________________________________________________
    # Calculate final value score
    if num_value_questions > 0:
        # Normalize by number of questions answered, similar to issue normalization
        final_value_score = (total_value_distance / num_value_questions) * weights['value_weight']
    else:
        # Apply penalty of 5 (middle of possible value range 0-9)
        final_value_score = 5 * weights['value_weight']

    # Calculate total score and round all scores
    return {
        'issue_score': round(final_issue_score, 2),
        'action_score': round(final_action_score, 2),
        'value_score': round(final_value_score, 2),
        'total_score': round(final_issue_score + final_action_score + final_value_score, 2)
    }

##_______________________________________________________________
##_______________________________________________________________
##_______________________________________________________________

# Test the function with example data
if __name__ == "__main__":
    # Example data (previous test data)
    new_user = {
        "Ocean Conservation": 1,
        "Mental Health": 2,
        "LGBTQ Rights": 3
    }

    new_org = {
        "Ocean Conservation": 1,
        "Depression Awareness": 2,
        "Marriage Equality": 3,
        "Gender Identity": 4
    }

    new_user_actions = ["volunteer", "donate", "social media"]
    new_org_actions = ["volunteer", "lobby", "campaign", "social media"]

    new_issue_categories = {
        "Ocean Conservation": "Environmental",
        "Mental Health": "Healthcare",
        "Depression Awareness": "Healthcare",
        "LGBTQ Rights": "Civil Rights",
        "Marriage Equality": "Civil Rights",
        "Gender Identity": "Civil Rights"
    }

    # New value questions data
    new_user_values = {
        "Ocean Conservation": {
            "q1": 8,  # Leans toward public government responsibility
            "q2": 9   # Strongly supports public funding
        },
        "Mental Health": {
            "q1": 7,
            "q2": 8
        }
    }

    new_org_values = {
        "Ocean Conservation": {
            "q1": 7,  # Also leans toward public government responsibility
            "q2": 8   # Also supports public funding
        },
        "Depression Awareness": {
            "q1": 6,
            "q2": 7
        }
    }

    # Calculate with default weights
    results = calculate_total_score(
        new_user,
        new_org,
        new_issue_categories,
        new_user_actions,
        new_org_actions,
        new_user_values,
        new_org_values
    )
    print("Results with default weights:", results)

    # Calculate with custom weights
    custom_weights = {
        'exact_match': 0.8,
        'category_match': 0.2,
        'issue_weight': 0.5,
        'action_weight': 0.3,
        'value_weight': 0.2
    }
    
    results_custom = calculate_total_score(
        new_user,
        new_org,
        new_issue_categories,
        new_user_actions,
        new_org_actions,
        new_user_values,
        new_org_values,
        custom_weights
    )
    print("\nResults with custom weights:", results_custom)