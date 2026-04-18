# Script to remove global Quick Stats from app.py
with open(r"e:\Ready projects\ML NLPready\Create Interactive Dashboards with Streamlit and Python\app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Lines to keep: 1-36, then replace 37-51 with just sentiment counting, then 52 onwards
new_content = lines[:36]  # Keep up to line 36

# Add the replacement (just sentiment counting without the UI)
new_content.append("\n")
new_content.append("# Count sentiments (we'll use these in different sections)\n")
new_content.append("negative_count = len(data[data['airline_sentiment'] == 'negative'])\n")
new_content.append("neutral_count = len(data[data['airline_sentiment'] == 'neutral'])\n") 
new_content.append("positive_count = len(data[data['airline_sentiment'] == 'positive'])\n")
new_content.append("\n")

# Add rest of the file from line 52 onwards
new_content.extend(lines[51:])  # Lines 52 onwards (index 51+)

# Write back
with open(r"e:\Ready projects\ML NLPready\Create Interactive Dashboards with Streamlit and Python\app.py", "w", encoding="utf-8") as f:
    f.writelines(new_content)

print("✅ Quick Stats removed from global view - now only in Overall Sentiment section!")
