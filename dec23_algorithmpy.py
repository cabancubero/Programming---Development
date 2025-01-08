##### Sample data
user = { "max_rank": 10, "rankings_by_category":
        {"Environmental": 
            {"environmental_racism": 1,
             "climate_change": 4,
             "ocean_conservation": 7 }},

        "Racism and Racial Prejudice":
            {"anti-blackness": 3,
             "critical race theory": 2 }}

organization = {
    "max_rank": 5,  # Note: Will be scaled to 10
    "rankings_by_category": {
        "Environmental": {
            "climate_change": 1,          # Top priority (scales to 2)
            "environmental_racism": 2,     # High priority (scales to 4)
            "deforestation": 4            # Lower priority (scales to 8)
        }
    }
}


## Missing category_to_issues dictionary

#### Category Pre-Computation Example 

category_ranking_differences = {}

# For org's climate_change (rank 1 * 2 = 2):
differences = [
    abs(1 - 2),  # vs user's environmental_racism (1): diff = 1
    abs(4 - 2),  # vs user's climate_change (4): diff = 2
    abs(7 - 2)   # vs user's ocean_conservation (7): diff = 5
]
category_ranking_differences["climate_change"] = [1, 2, 5]

# For org's environmental_racism (rank 2 * 2 = 4):
differences = [
    abs(1 - 4),  # vs user's environmental_racism (1): diff = 3
    abs(4 - 4),  # vs user's climate_change (4): diff = 0
    abs(7 - 4)   # vs user's ocean_conservation (7): diff = 3
]
category_ranking_differences["environmental_racism"] = [3, 0, 3]

# For org's deforestation (rank 4 * 2 = 8):
differences = [
    abs(1 - 8),  # vs user's environmental_racism (1): diff = 7
    abs(4 - 8),  # vs user's climate_change (4): diff = 4
    abs(7 - 8)   # vs user's ocean_conservation (7): diff = 1
]
category_ranking_differences["deforestation"] = [7, 4, 1]



#####  Algorithm Section

def calculate_match_score( #should this be a class instead?
    user: dict,
    organization: dict,
    category_to_issues: dict,
    issue_weight: float = 0.7,
    action_weight: float = 0.3,
    exact_match_ratio: float = 0.7
) -> float:
    """
    Calculate match score with optimized category matching.
    """
    def calculate_issue_score():
        scale_factor = user["max_rank"] / organization["max_rank"]
        total_issue_distance = 0
        number_of_comparisons = 0

        # Examine each category and its issues
        for category in category_to_issues:#
            org_category_rankings = organization["rankings_by_category"].get(category, {})
            user_category_rankings = user["rankings_by_category"].get(category, {})
            
            if not org_category_rankings:
                continue
                
            # Pre-compute all possible ranking differences for this category
            # This prevents nested iteration later
            category_ranking_differences = {}
            for org_issue_id, org_rank in org_category_rankings.items():
                scaled_org_rank = org_rank * scale_factor
                for user_issue_id, user_rank in user_category_rankings.items():
                    difference = abs(user_rank - scaled_org_rank)
                    # Store the difference keyed by org_issue_id
                    if org_issue_id not in category_ranking_differences:
                        category_ranking_differences[org_issue_id] = []
                    category_ranking_differences[org_issue_id].append(difference)

            # Now process each issue using our pre-computed differences
            for issue_id in category_to_issues[category]:
                org_rank = org_category_rankings.get(issue_id)
                if org_rank is None:
                    continue
                
                number_of_comparisons += 1
                
                # Check for exact match
                exact_distance = user["max_rank"]
                if issue_id in user_category_rankings:
                    user_rank = user_category_rankings[issue_id]
                    exact_distance = abs(user_rank - org_rank * scale_factor)
                
                # Get categorical match from pre-computed differences
                category_distance = user["max_rank"]
                if issue_id in category_ranking_differences:
                    category_distance = min(category_ranking_differences[issue_id])
                
                # Combine distances for this issue
                issue_distance = (exact_distance * exact_match_ratio + 
                                category_distance * (1 - exact_match_ratio))
                total_issue_distance += issue_distance

        return total_issue_distance / (number_of_comparisons or 1)

    # Action scoring remains the same
    def calculate_action_score():
        user_actions = set(user["actions"])
        org_actions = set(organization["actions"])
        
        if user_actions and org_actions:
            action_intersection = len(user_actions & org_actions)
            action_union = len(user_actions | org_actions)
            action_similarity = action_intersection / action_union
            return (1 - action_similarity) * user["max_rank"]
        return user["max_rank"]

    # Calculate and combine scores
    issue_score = calculate_issue_score()
    action_score = calculate_action_score()
    
    final_score = (issue_score * issue_weight + 
                  action_score * action_weight)
    
    return final_score / user["max_rank"]