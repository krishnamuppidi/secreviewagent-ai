"""
GitHub Webhook Server for SecReviewAgent.

Receives PR events and triggers security reviews.
"""

import hashlib
import hmac
import os
from typing import Any

import httpx
from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel

from secreviewagent.agents.review_agent import SecReviewAgent

app = FastAPI(
    title="SecReviewAgent Webhook",
    description="Educational IaC Security Review Agent for GitHub PRs",
    version="0.1.0",
)

# Configuration
WEBHOOK_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")


class PREvent(BaseModel):
    """GitHub PR event payload (simplified)."""
    
    action: str
    number: int
    pull_request: dict
    repository: dict


def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify GitHub webhook signature."""
    if not WEBHOOK_SECRET:
        return True  # Skip verification if no secret configured
    
    expected = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)


async def get_pr_diff(repo: str, pr_number: int) -> str:
    """Fetch PR diff from GitHub."""
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    headers = {
        "Accept": "application/vnd.github.v3.diff",
        "Authorization": f"Bearer {GITHUB_TOKEN}" if GITHUB_TOKEN else "",
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.text


async def post_review_comment(repo: str, pr_number: int, body: str) -> None:
    """Post a review comment on the PR."""
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json={"body": body})
        response.raise_for_status()


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "secreviewagent"}


@app.post("/webhook/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None),
    x_github_event: str = Header(None),
):
    """
    Handle GitHub webhook events.
    
    Triggers on:
    - pull_request.opened
    - pull_request.synchronize (new commits pushed)
    """
    payload = await request.body()
    
    # Verify signature
    if x_hub_signature_256 and not verify_signature(payload, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse event
    data = await request.json()
    
    # Only process PR events
    if x_github_event != "pull_request":
        return {"status": "ignored", "reason": f"Event type: {x_github_event}"}
    
    action = data.get("action")
    if action not in ("opened", "synchronize"):
        return {"status": "ignored", "reason": f"Action: {action}"}
    
    pr_number = data["number"]
    repo = data["repository"]["full_name"]
    
    # Check if PR contains IaC files
    pr_files = data.get("pull_request", {}).get("changed_files", 0)
    
    try:
        # Get PR diff
        diff = await get_pr_diff(repo, pr_number)
        
        # Check if it contains Terraform or K8s files
        if not any(ext in diff for ext in [".tf", ".yaml", ".yml"]):
            return {"status": "skipped", "reason": "No IaC files in PR"}
        
        # Determine IaC type
        iac_type = "terraform" if ".tf" in diff else "kubernetes"
        
        # Run analysis
        agent = SecReviewAgent()
        result = agent.review_pr_diff(diff, iac_type)
        
        # Format and post comment
        comment = f"""## 🔐 SecReviewAgent Security Analysis

{agent.format_review_markdown(result)}

---
*Automated security review by [SecReviewAgent AI](https://github.com/krishnamuppidi/secreviewagent-ai)*
"""
        
        if GITHUB_TOKEN:
            await post_review_comment(repo, pr_number, comment)
            return {"status": "reviewed", "pr": pr_number, "repo": repo}
        else:
            return {
                "status": "analyzed",
                "pr": pr_number,
                "repo": repo,
                "note": "No GITHUB_TOKEN - comment not posted",
                "review": result.architecture_summary,
            }
    
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.post("/analyze")
async def analyze_endpoint(
    directory: str = None,
    diff: str = None,
    iac_type: str = "terraform",
):
    """
    Direct analysis endpoint (for testing without GitHub).
    
    Provide either a directory path or a diff string.
    """
    agent = SecReviewAgent()
    
    if diff:
        result = agent.review_pr_diff(diff, iac_type)
    elif directory:
        if iac_type == "terraform":
            result = agent.review_terraform_directory(directory)
        else:
            result = agent.review_kubernetes_directory(directory)
    else:
        raise HTTPException(status_code=400, detail="Provide either 'directory' or 'diff'")
    
    return {
        "architecture_summary": result.architecture_summary,
        "findings_count": len(result.security_findings),
        "review_markdown": agent.format_review_markdown(result),
    }
