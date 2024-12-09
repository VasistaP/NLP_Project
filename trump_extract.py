
import praw
import time
import pandas as pd
from datetime import datetime, timezone

# Initialize Reddit API client
reddit = praw.Reddit(
    client_id="54e-0s9m_UCxWKHyE6q7Pg",
    client_secret="Oh4SK1yYzAxhPLIgkh-PUMU3aGhrZw",
    user_agent="elnlp"
)

def is_within_timeframe(timestamp):
    """Check if the post/comment timestamp is within the specified date range."""
    start_date = datetime(2024, 7, 23, tzinfo=timezone.utc)
    end_date = datetime(2024, 11, 5, tzinfo=timezone.utc)
    post_date = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    return start_date <= post_date <= end_date

def collect_comments(subreddit_name, keywords, max_comments=5000):
    """Collect comments from a subreddit based on keyword search."""
    comments_data = []
    
    print(f"Started collecting comments from r/{subreddit_name} at: {datetime.now()}")
    
    try:
        # Use subreddit search to find relevant comments
        for submission in reddit.subreddit(subreddit_name).search(" OR ".join(keywords), sort="new", limit=None):  
            print(f"Processing submission ID: {submission.id}, Title: {submission.title}")  # Debugging line
            
            submission.comments.replace_more(limit=0)  # Fetch all comments for this submission
            for comment in submission.comments.list():
                # Check if the comment is within the timeframe
                if is_within_timeframe(comment.created_utc):
                    comment_body = comment.body.lower()
                    # Check if any keyword is in the comment body
                    if any(keyword in comment_body for keyword in keywords):
                        comments_data.append({
                            "id": comment.id,
                            "post_id": submission.id,
                            "body": comment.body,
                            "score": comment.score,
                            "created_utc": datetime.fromtimestamp(comment.created_utc, tz=timezone.utc)
                        })

                        # Stop if we reach the maximum number of comments
                        if len(comments_data) >= max_comments:
                            print("Reached maximum number of comments.")
                            break
            
            # Rate limiting: sleep to ensure we don't exceed 100 queries per minute
            time.sleep(0.6)  # Sleep for approximately 0.6 seconds to stay within limits
            
            if len(comments_data) >= max_comments:
                break
        
        print(f"Finished collecting comments at: {datetime.now()}")
        print(f"Total comments collected: {len(comments_data)}")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return comments_data

# Define a broader set of keywords related to trump
trump_keywords = [
    "donald trump", 
    "trump campaign", 
    "trump 2024", 
    "trump", 
    "republican candidate", 
    "former president trump",
    "mar-a-lago"
    "donald"
]

# Main loop to collect up to 5000 comments across multiple runs
all_comments = []
target_comments = 5000

while len(all_comments) < target_comments:
    print(f"Current total comments collected: {len(all_comments)}")
    
    # Collect comments from r/politics using search functionality
    new_comments = collect_comments("politics", trump_keywords)
    
    all_comments.extend(new_comments)  # Append newly collected comments
    
    # Save to CSV file after each run to avoid data loss
    pd.DataFrame(all_comments).to_csv("trump_comments.csv", index=False)
    
    if len(all_comments) >= target_comments:
        print("Target number of comments reached.")
        break

print(f"Final total comments collected: {len(all_comments)}")
