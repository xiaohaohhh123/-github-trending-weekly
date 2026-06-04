"""
Email sender using Resend API (https://resend.com).
Free tier: 100 emails/day, perfect for getting started.
"""
import os
import json
import resend
from dotenv import load_dotenv

load_dotenv()

SUBSCRIBERS_FILE = os.path.join(
    os.path.dirname(__file__), "..", "data", "subscribers.json"
)


def _init_resend():
    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        raise RuntimeError("RESEND_API_KEY not set in .env")
    resend.api_key = api_key


def load_subscribers() -> list[dict]:
    """Load subscribers from the JSON file."""
    if not os.path.exists(SUBSCRIBERS_FILE):
        return []
    with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def send_newsletter(
    html: str,
    subject: str,
    from_email: str = "GitHubTrending <newsletter@githubtrending.cn>",
    test_mode: bool = True,
) -> dict:
    """
    Send the newsletter to all subscribers via Resend.
    In test mode, only sends to the first subscriber (you).
    """
    _init_resend()
    subscribers = load_subscribers()

    if not subscribers:
        print("[sender] No subscribers found. Add yourself to data/subscribers.json first!")
        return {"sent": 0, "total": 0}

    if test_mode:
        subscribers = subscribers[:1]
        print(f"[sender] TEST MODE - sending only to {subscribers[0]['email']}")

    results = {"sent": 0, "failed": 0, "total": len(subscribers)}
    for sub in subscribers:
        try:
            resend.Emails.send({
                "from": from_email,
                "to": [sub["email"]],
                "subject": subject,
                "html": html,
            })
            results["sent"] += 1
            print(f"[sender] OK Sent to {sub['email']}")
        except Exception as e:
            results["failed"] += 1
            print(f"[sender] FAILED {sub['email']}: {e}")

    print(f"[sender] Done! {results['sent']}/{results['total']} sent, {results['failed']} failed")
    return results
