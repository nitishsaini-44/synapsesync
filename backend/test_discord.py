import sys
import json
from backend.services.openai_service import summarize_message, classify_lead, generate_reply
from backend.services.discord_service import DiscordService

message = """Dear Participant,

Thank you for your participation in the GridLock 2.0 Hackathon organized by Flipkart. We appreciate the enthusiasm, effort, and innovation demonstrated by you throughout the competition.

As part of our standard competition process, all shortlisted submissions will undergo a comprehensive verification and reproducibility review before final results are announced.

Participants are required to submit their source code and .ipynb files used to generate their leaderboard submissions. Our review process will verify that submitted results can be reproduced using the provided code and that all competition rules have been followed.

Please note that leaderboard rankings alone do not determine final selection. Any submission that cannot be successfully reproduced or is found to be in violation of the competition guidelines may be disqualified during the verification stage.

We appreciate your cooperation and understanding as we work to ensure a fair, transparent, and merit-based evaluation process for all participants.

Best Regards,
HackerEarth"""

print("Running Summary...")
summary_result = summarize_message(message)
print("Running Classify...")
classify_result = classify_lead(message)
print("Running Auto Reply...")
reply_result = generate_reply(message, category=classify_result.get('category'))

discord_message = f"""**Hackathon Message Workflow Results:**

**1. Summary Result:**
- Summary: {summary_result.get('summary')}
- Category: {summary_result.get('category')}
- Urgency: {summary_result.get('urgency')}

**2. Classify Result:**
- Summary: {classify_result.get('summary')}
- Category: {classify_result.get('category')}
- Priority: {classify_result.get('priority')}

**3. Auto Reply Generated:**
{reply_result.get('reply')}
"""

print("\nSending to Discord:\n")
print(discord_message)

from flask import Flask
from backend.config import Config
app = Flask(__name__)
app.config.from_object(Config)

with app.app_context():
    success, result_message = DiscordService.send_notification(discord_message)
    if success:
        print("Successfully sent to Discord!")
    else:
        print(f"Failed to send: {result_message}")
        sys.exit(1)
