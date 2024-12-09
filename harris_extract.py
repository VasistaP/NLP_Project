
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

def collect_comments_from_submissions(subreddit_name, keywords, max_comments=5000, seen_ids=None, processed_submissions=None):
    """Collect comments from relevant submissions in a subreddit."""
    if seen_ids is None:
        seen_ids = set()
    if processed_submissions is None:
        processed_submissions = set()

    comments_data = []
    print(f"Started collecting comments from r/{subreddit_name} at: {datetime.now()}")

    skipping_flag = False  # To control "Skipping..." messages

    try:
        for submission in reddit.subreddit(subreddit_name).top(time_filter="year", limit=None):  # Fetch top submissions from past year
  # Fetch top submissions from past year
            # Skip already processed submissions
            if submission.id in processed_submissions:
                continue

            # Check if the submission itself falls within the timeframe
            if not is_within_timeframe(submission.created_utc):
                if not skipping_flag:
                    print("Skipping...")  # Print "Skipping..." only once
                    skipping_flag = True
                continue

            # Reset skipping flag as we've reached relevant submissions
            skipping_flag = False

            print(f"Processing submission ID: {submission.id}, Title: {submission.title}")  # Detailed log
            
            submission.comments.replace_more(limit=0)  # Fetch all comments for this submission
            for comment in submission.comments.list():
                if comment.id not in seen_ids:
                    if is_within_timeframe(comment.created_utc):  # Check comment's timestamp
                        comment_body = comment.body.lower()
                        if any(keyword in comment_body for keyword in keywords):
                            comments_data.append({
                                "id": comment.id,
                                "post_id": submission.id,
                                "body": comment.body,
                                "score": comment.score,
                                "created_utc": datetime.fromtimestamp(comment.created_utc, tz=timezone.utc)
                            })
                            seen_ids.add(comment.id)  # Mark comment as processed
                            print(f"Added comment ID: {comment.id}")  # Debugging line

                            # Stop if we reach the maximum number of comments
                            if len(comments_data) >= max_comments:
                                print("Reached maximum number of comments.")
                                break
            
            processed_submissions.add(submission.id)  # Mark submission as processed

            # Rate limiting to avoid hitting API limits
            time.sleep(0.6)

            if len(comments_data) >= max_comments:
                break

        print(f"Finished collecting comments at: {datetime.now()}")
        print(f"Total comments collected: {len(comments_data)}")

    except Exception as e:
        print(f"An error occurred: {e}")
    
    return comments_data, seen_ids, processed_submissions

# Define keywords for Harris
kamala_harris_keywords = [
    "kamala harris", "vice president harris", "kamala", 
    "2024 kamala harris", "harris 2024", "harris campaign", 
    "kamala harris election", "democratic candidate", 
    "vice president", "harris", "kamala"
]

# Main loop to collect up to 5000 comments
all_comments = []
seen_ids = set()  # Track seen comment IDs
processed_submissions = set()  # Track processed submission IDs
target_comments = 5000
last_collected = time.time()

while len(all_comments) < target_comments:
    print(f"Current total comments collected: {len(all_comments)}")
    
    # Collect comments from relevant submissions
    new_comments, seen_ids, processed_submissions = collect_comments_from_submissions(
        "politics", kamala_harris_keywords, max_comments=target_comments - len(all_comments),
        seen_ids=seen_ids, processed_submissions=processed_submissions
    )
    
    if new_comments:
        all_comments.extend(new_comments)
        last_collected = time.time()  # Reset timer
        # Save progress to avoid data loss
        pd.DataFrame(all_comments).drop_duplicates(subset="id").to_csv("increased_harris_comments.csv", index=False)
    else:
        elapsed_time = time.time() - last_collected
        print(f"No new comments in the last {elapsed_time:.2f} seconds.")
        if elapsed_time > 300:  # Stop after 5 minutes of inactivity
            print("No new comments for a while. Stopping the script.")
            break

    if len(all_comments) >= target_comments:
        print("Target number of comments reached.")
        break

print(f"Final total comments collected: {len(all_comments)}")