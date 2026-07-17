"""
SecReviewAgent Lambda Handler.

Receives GitHub webhook events, analyzes PR diffs with full repo context,
and posts educational review comments.

KEY FEATURE: Persistent repo memory in S3
- First PR: Scans entire repo, builds architecture understanding, saves to S3
- Subsequent PRs: Loads context, explains changes in full architecture context
"""

import hashlib
import hmac
import json
import os
import base64
from typing import Any

import anthropic
import boto3
import httpx


# AWS clients
secrets_client = boto3.client("secretsmanager")
s3_client = boto3.client("s3")

# Config
MEMORY_BUCKET = os.environ.get("MEMORY_BUCKET", "secreviewagent-memory")
SECRET_NAME = os.environ.get("SECRET_NAME", "secreviewagent/config")

# Cached secrets
_SECRETS = None


def get_secrets() -> dict:
    """Fetch secrets from AWS Secrets Manager."""
    global _SECRETS
    if _SECRETS is None:
        response = secrets_client.get_secret_value(SecretId=SECRET_NAME)
        _SECRETS = json.loads(response["SecretString"])
    return _SECRETS


def get_repo_memory(repo: str) -> dict | None:
    """Load repo context from S3."""
    key = f"{repo.replace('/', '-')}/context.json"
    try:
        response = s3_client.get_object(Bucket=MEMORY_BUCKET, Key=key)
        return json.loads(response["Body"].read().decode("utf-8"))
    except s3_client.exceptions.NoSuchKey:
        return None
    except Exception as e:
        print(f"Error loading repo memory: {e}")
        return None


def save_repo_memory(repo: str, context: dict) -> None:
    """Save repo context to S3."""
    key = f"{repo.replace('/', '-')}/context.json"
    try:
        s3_client.put_object(
            Bucket=MEMORY_BUCKET,
            Key=key,
            Body=json.dumps(context, indent=2),
            ContentType="application/json",
        )
        print(f"Saved repo memory for {repo}")
    except Exception as e:
        print(f"Error saving repo memory: {e}")


def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify GitHub webhook signature."""
    secrets = get_secrets()
    webhook_secret = secrets.get("GITHUB_WEBHOOK_SECRET", "")
    
    if not webhook_secret:
        return True
    
    expected = "sha256=" + hmac.new(
        webhook_secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)


def github_request(endpoint: str, headers_extra: dict = None) -> Any:
    """Make authenticated GitHub API request."""
    secrets = get_secrets()
    token = secrets.get("GITHUB_TOKEN", "")
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {token}" if token else "",
        "User-Agent": "SecReviewAgent/1.0",
    }
    if headers_extra:
        headers.update(headers_extra)
    
    response = httpx.get(f"https://api.github.com{endpoint}", headers=headers, timeout=30)
    response.raise_for_status()
    return response


def get_pr_diff(repo: str, pr_number: int) -> str:
    """Fetch PR diff from GitHub."""
    response = github_request(
        f"/repos/{repo}/pulls/{pr_number}",
        {"Accept": "application/vnd.github.v3.diff"}
    )
    return response.text


def get_pr_files(repo: str, pr_number: int) -> list:
    """Get list of changed files in PR."""
    response = github_request(f"/repos/{repo}/pulls/{pr_number}/files")
    return response.json()


def get_repo_tree(repo: str, branch: str = "main") -> list:
    """Get full file tree of a repo."""
    try:
        response = github_request(f"/repos/{repo}/git/trees/{branch}?recursive=1")
        return response.json().get("tree", [])
    except Exception as e:
        print(f"Error getting repo tree: {e}")
        return []


def get_file_content(repo: str, path: str, branch: str = "main") -> str | None:
    """Fetch a single file's content from GitHub."""
    try:
        response = github_request(f"/repos/{repo}/contents/{path}?ref={branch}")
        data = response.json()
        if data.get("encoding") == "base64":
            return base64.b64decode(data["content"]).decode("utf-8")
        return data.get("content", "")
    except Exception as e:
        print(f"Error fetching {path}: {e}")
        return None


def scan_repo_iac(repo: str, branch: str = "main") -> dict:
    """
    Scan entire repo for IaC files and build architecture understanding.
    Returns a context dict with architecture summary and resource inventory.
    """
    print(f"Scanning repo {repo} for IaC files...")
    
    tree = get_repo_tree(repo, branch)
    
    # Find IaC files
    iac_files = []
    for item in tree:
        if item["type"] == "blob":
            path = item["path"]
            if path.endswith(".tf") or (path.endswith((".yaml", ".yml")) and "k8s" in path.lower()):
                iac_files.append(path)
    
    if not iac_files:
        return {"error": "No IaC files found", "files": []}
    
    # Fetch content of IaC files (limit to avoid timeout)
    iac_content = {}
    for path in iac_files[:20]:  # Limit to 20 files
        content = get_file_content(repo, path, branch)
        if content:
            iac_content[path] = content[:5000]  # Truncate large files
    
    # Use LLM to build architecture understanding
    secrets = get_secrets()
    client = anthropic.Anthropic(api_key=secrets.get("ANTHROPIC_API_KEY"))
    
    system_prompt = """You are analyzing Infrastructure-as-Code to build a concise architecture summary.
Your output will be stored and used as context for future PR reviews.

OUTPUT FORMAT (JSON):
{
  "architecture_summary": "2-3 paragraph description of what this infrastructure does, in plain English",
  "components": [
    {
      "name": "Component name (e.g., 'Event Processing Lambda')",
      "type": "Resource type (e.g., 'aws_lambda_function')",
      "purpose": "What it does",
      "connections": ["Other components it connects to"]
    }
  ],
  "data_flows": [
    "User -> API Gateway -> Lambda -> DynamoDB",
    "..."
  ],
  "security_notes": ["Existing security configurations worth noting"],
  "tech_stack": ["AWS Lambda", "DynamoDB", "API Gateway", ...]
}"""

    files_content = "\n\n".join([
        f"=== {path} ===\n{content}"
        for path, content in iac_content.items()
    ])
    
    prompt = f"""Analyze this repository's Infrastructure-as-Code and create a concise architecture summary.

IaC FILES:
{files_content[:30000]}

Create a summary that will help future PR reviewers understand the full context of this application."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
        )
        
        response_text = response.content[0].text
        
        # Extract JSON
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        
        context = json.loads(response_text)
        context["_meta"] = {
            "repo": repo,
            "branch": branch,
            "files_scanned": list(iac_content.keys()),
            "scan_time": __import__("datetime").datetime.utcnow().isoformat(),
        }
        return context
    
    except Exception as e:
        print(f"Error building repo context: {e}")
        return {
            "error": str(e),
            "files": list(iac_content.keys()),
        }


def analyze_pr_with_context(
    repo: str,
    pr_number: int,
    diff: str,
    changed_files: list,
    repo_context: dict | None,
) -> dict:
    """
    Analyze PR diff with full repo context.
    """
    secrets = get_secrets()
    client = anthropic.Anthropic(api_key=secrets.get("ANTHROPIC_API_KEY"))
    
    # Build context section
    if repo_context and "architecture_summary" in repo_context:
        context_section = f"""
EXISTING ARCHITECTURE CONTEXT:
{repo_context.get('architecture_summary', 'No summary available')}

EXISTING COMPONENTS:
{json.dumps(repo_context.get('components', []), indent=2)[:3000]}

DATA FLOWS:
{chr(10).join(repo_context.get('data_flows', ['No data flows documented']))}

TECH STACK: {', '.join(repo_context.get('tech_stack', ['Unknown']))}
"""
    else:
        context_section = """
NOTE: This is the first PR review for this repo - no existing architecture context available.
The review will focus on the changes themselves.
"""

    system_prompt = """You are SecReviewAgent, an educational security review assistant.

You have CONTEXT about the existing architecture of this repo. Use it to explain how the PR changes fit into the bigger picture.

Your audience is security practitioners who may not be deeply familiar with cloud services.

OUTPUT FORMAT (JSON):
{
  "summary": "What this PR does in context of the full architecture",
  "architecture_impact": "How these changes affect the existing architecture",
  "changes_explained": [
    {"file": "filename", "change": "what changed", "context": "how it relates to existing components"}
  ],
  "security_findings": [
    {
      "severity": "critical|high|medium|low|info",
      "title": "Short title",
      "description": "Detailed explanation with architecture context",
      "recommendation": "What to do"
    }
  ],
  "approval_recommendation": "approve|request_changes|comment",
  "approval_reason": "Why, considering the full architecture"
}"""

    files_context = "\n".join([
        f"- {f['filename']} ({f['status']}, +{f['additions']}/-{f['deletions']})"
        for f in changed_files[:20]
    ])
    
    prompt = f"""{context_section}

PR CHANGES:
Files changed:
{files_context}

Diff:
```diff
{diff[:15000]}
```

Analyze these changes IN CONTEXT of the existing architecture. Explain:
1. What components are being added/modified?
2. How do they connect to existing components?
3. What are the security implications?

Respond with valid JSON only."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}],
    )
    
    response_text = response.content[0].text
    
    if "```json" in response_text:
        start = response_text.find("```json") + 7
        end = response_text.find("```", start)
        response_text = response_text[start:end].strip()
    
    return json.loads(response_text)


def post_pr_comment(repo: str, pr_number: int, body: str) -> None:
    """Post a comment on the PR."""
    secrets = get_secrets()
    token = secrets.get("GITHUB_TOKEN")
    
    if not token:
        print("No GITHUB_TOKEN - skipping comment")
        return
    
    response = httpx.post(
        f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments",
        headers={
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "SecReviewAgent/1.0",
        },
        json={"body": body},
        timeout=30,
    )
    response.raise_for_status()


def format_review_comment(analysis: dict, has_context: bool) -> str:
    """Format analysis as a GitHub PR comment."""
    lines = ["## 🔐 SecReviewAgent Security Review\n"]
    
    # Context indicator
    if has_context:
        lines.append("*📚 Review includes full architecture context*\n")
    else:
        lines.append("*🆕 First review for this repo - context will be built for future PRs*\n")
    
    # Summary
    lines.append(f"**Summary:** {analysis.get('summary', 'Analysis complete.')}\n")
    
    # Architecture impact (new!)
    if analysis.get("architecture_impact"):
        lines.append(f"**Architecture Impact:** {analysis['architecture_impact']}\n")
    
    # Changes explained
    if analysis.get("changes_explained"):
        lines.append("### 📝 Changes Explained\n")
        for change in analysis["changes_explained"]:
            lines.append(f"**`{change.get('file', 'unknown')}`**")
            lines.append(f"- {change.get('change', '')}")
            if change.get("context"):
                lines.append(f"- *Architecture context:* {change['context']}")
            lines.append("")
    
    # Security findings
    findings = analysis.get("security_findings", [])
    if findings:
        lines.append("### 🛡️ Security Findings\n")
        emoji_map = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵", "info": "ℹ️"}
        
        for finding in findings:
            severity = finding.get("severity", "info")
            emoji = emoji_map.get(severity, "ℹ️")
            lines.append(f"{emoji} **[{severity.upper()}] {finding.get('title', 'Finding')}**")
            lines.append(f"> {finding.get('description', '')}")
            if finding.get("recommendation"):
                lines.append(f"> **Fix:** {finding['recommendation']}")
            lines.append("")
    else:
        lines.append("### ✅ No Security Issues Found\n")
    
    # Recommendation
    rec = analysis.get("approval_recommendation", "comment")
    reason = analysis.get("approval_reason", "")
    rec_emoji = {"approve": "✅", "request_changes": "🚫", "comment": "💬"}
    lines.append(f"### {rec_emoji.get(rec, '💬')} Recommendation: **{rec.upper()}**")
    if reason:
        lines.append(f"_{reason}_")
    
    lines.append("\n---")
    lines.append("*Automated review by [SecReviewAgent AI](https://github.com/krishnamuppidi/secreviewagent-ai)*")
    
    return "\n".join(lines)


def handler(event: dict, context: Any) -> dict:
    """Lambda handler for GitHub webhook events."""
    print(f"Event received")
    
    # Parse request
    headers = event.get("headers", {})
    body = event.get("body", "")
    
    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode("utf-8")
    
    # Verify signature
    signature = headers.get("x-hub-signature-256") or headers.get("X-Hub-Signature-256", "")
    if signature and not verify_signature(body.encode(), signature):
        return {"statusCode": 401, "body": json.dumps({"error": "Invalid signature"})}
    
    # Check event type
    event_type = headers.get("x-github-event") or headers.get("X-GitHub-Event", "")
    
    if event_type != "pull_request":
        return {"statusCode": 200, "body": json.dumps({"status": "ignored", "reason": f"Event: {event_type}"})}
    
    # Parse payload
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return {"statusCode": 400, "body": json.dumps({"error": "Invalid JSON"})}
    
    action = payload.get("action", "")
    if action not in ("opened", "synchronize"):
        return {"statusCode": 200, "body": json.dumps({"status": "ignored", "reason": f"Action: {action}"})}
    
    pr = payload.get("pull_request", {})
    repo = payload.get("repository", {}).get("full_name", "")
    pr_number = payload.get("number", 0)
    base_branch = pr.get("base", {}).get("ref", "main")
    
    print(f"Processing PR #{pr_number} in {repo}")
    
    try:
        # Get PR files and diff
        files = get_pr_files(repo, pr_number)
        iac_files = [f for f in files if f["filename"].endswith((".tf", ".yaml", ".yml"))]
        
        if not iac_files:
            return {"statusCode": 200, "body": json.dumps({"status": "skipped", "reason": "No IaC files"})}
        
        diff = get_pr_diff(repo, pr_number)
        
        # Load or build repo context
        repo_context = get_repo_memory(repo)
        has_context = repo_context is not None
        
        if not has_context:
            print(f"No existing context for {repo}, scanning repo...")
            repo_context = scan_repo_iac(repo, base_branch)
            if "error" not in repo_context:
                save_repo_memory(repo, repo_context)
                has_context = True
        
        # Analyze PR with context
        analysis = analyze_pr_with_context(repo, pr_number, diff, files, repo_context)
        
        # Post comment
        comment = format_review_comment(analysis, has_context)
        post_pr_comment(repo, pr_number, comment)
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "reviewed",
                "pr": pr_number,
                "repo": repo,
                "has_context": has_context,
                "findings": len(analysis.get("security_findings", [])),
            })
        }
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
