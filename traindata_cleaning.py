import pandas as pd
import re
import nltk

# Ensure necessary NLTK data is downloaded
nltk.download('punkt')

# Load the datasets
biden_df = pd.read_csv('biden_stance_train_public.csv')  # Adjust file name as necessary
trump_df = pd.read_csv('trump_stance_train_public.csv')  # Adjust file name as necessary

# Add a 'candidate' column to each dataset
biden_df['candidate'] = 'Biden'
trump_df['candidate'] = 'Trump'

def preprocess_text_basic(text):
    """
    Perform basic cleaning (remove HTML tags, URLs, excessive whitespaces).
    No stopword removal, stemming, or lemmatization.
    """
    # Remove URLs (http, https, and www links)
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    # Remove extra spaces between words (convert multiple spaces to a single space)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Convert text to lowercase (optional, for consistency)
    text = text.lower()
    
    return text

# Apply basic preprocessing to both Biden and Trump data
biden_df['processed_text'] = biden_df['text'].apply(preprocess_text_basic)
trump_df['processed_text'] = trump_df['text'].apply(preprocess_text_basic)

# Combine the datasets
combined_df = pd.concat([biden_df, trump_df], ignore_index=True)

# Handle missing values
combined_df.dropna(subset=['processed_text', 'label'], inplace=True)

# Reset index after concatenation
combined_df.reset_index(drop=True, inplace=True)

# Normalize labels (if necessary)
combined_df['label'] = combined_df['label'].str.strip().str.upper()

# Map labels to numeric values (if necessary)
label_mapping = {'AGAINST': 0, 'FAVOR': 1, 'NONE': 2}
combined_df['encoded_label'] = combined_df['label'].map(label_mapping)

# Drop unnecessary columns: 'tweet_id', 'text', 'label', and 'candidate'
combined_df.drop(columns=['tweet_id', 'text', 'label', 'candidate'], inplace=True, errors='ignore')

# Save the processed training data
combined_df.to_csv('combined_processed_tweets_basic_cleaning.csv', index=False)

print("Processed training dataset saved as 'combined_processed_tweets_basic_cleaning.csv'")

# Display some statistics
print(f"Total tweets: {len(combined_df)}")
print(f"Biden tweets: {len(combined_df[combined_df['candidate'] == 'Biden'])}")
print(f"Trump tweets: {len(combined_df[combined_df['candidate'] == 'Trump'])}")
print("\nSample processed tweets:")
print(combined_df[['processed_text', 'encoded_label']].head())
