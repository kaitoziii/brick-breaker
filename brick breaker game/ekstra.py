from leaderboard import get_top_scores

def show_leaderboard():
    top_scores = get_top_scores()
    print("\n=== Leaderboard ===")
    for i, (username, score) in enumerate(top_scores, 1):
        print(f"{i}. {username} - {score}")
