#!/usr/bin/env python3
"""
Jira-Slack AI Agent

Monitors Slack channels for bug reports and task requests,
uses Claude AI to detect and classify them, then automatically
creates Jira tickets and sends notifications.
"""

import os
import logging
import json
import yaml
from typing import Dict, Optional, Tuple
from datetime import datetime

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from jira import JIRA
from anthropic import Anthropic
from dotenv import load_dotenv


class JiraSlackAgent:
    """Main agent class that coordinates Slack monitoring, AI detection, and Jira ticket creation."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the agent with configuration."""
        # Load environment variables
        load_dotenv()

        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Setup logging
        self._setup_logging()

        # Initialize clients
        self.slack_app = self._init_slack()
        self.jira_client = self._init_jira()
        self.anthropic_client = self._init_anthropic()

        # Register Slack event handlers
        self._register_handlers()

        self.logger.info("Jira-Slack Agent initialized successfully")

    def _setup_logging(self):
        """Configure logging."""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_file = log_config.get('file', 'agent.log')

        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _init_slack(self) -> App:
        """Initialize Slack app."""
        token = os.getenv('SLACK_BOT_TOKEN')
        signing_secret = os.getenv('SLACK_SIGNING_SECRET')

        if not token or not signing_secret:
            raise ValueError("SLACK_BOT_TOKEN and SLACK_SIGNING_SECRET must be set in .env file")

        app = App(token=token, signing_secret=signing_secret)
        self.logger.info("Slack app initialized")
        return app

    def _init_jira(self) -> JIRA:
        """Initialize Jira client."""
        jira_email = os.getenv('JIRA_EMAIL')
        jira_token = os.getenv('JIRA_API_TOKEN')
        jira_url = self.config['jira']['url']

        if not jira_email or not jira_token:
            raise ValueError("JIRA_EMAIL and JIRA_API_TOKEN must be set in .env file")

        jira = JIRA(
            server=jira_url,
            basic_auth=(jira_email, jira_token)
        )
        self.logger.info(f"Jira client initialized for {jira_url}")
        return jira

    def _init_anthropic(self) -> Anthropic:
        """Initialize Anthropic client."""
        api_key = os.getenv('ANTHROPIC_API_KEY')

        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set in .env file")

        client = Anthropic(api_key=api_key)
        self.logger.info("Anthropic client initialized")
        return client

    def _register_handlers(self):
        """Register Slack event handlers."""
        @self.slack_app.event("message")
        def handle_message(event, say, client):
            """Handle incoming Slack messages."""
            # Ignore bot messages and message subtypes (edits, deletes, etc.)
            if event.get('subtype') or event.get('bot_id'):
                return

            # Check if message is from a monitored channel
            channel_id = event.get('channel')
            channel_info = client.conversations_info(channel=channel_id)
            channel_name = channel_info['channel']['name']

            monitored_channels = self.config['slack']['monitored_channels']
            if channel_name not in monitored_channels:
                return

            # Process the message
            self._process_message(event, channel_name, client)

    def _process_message(self, event: Dict, channel_name: str, client):
        """Process a Slack message to determine if it should create a Jira ticket."""
        message_text = event.get('text', '')
        user_id = event.get('user')
        timestamp = event.get('ts')

        self.logger.info(f"Processing message from #{channel_name}: {message_text[:100]}...")

        try:
            # Use AI to analyze the message
            should_create, ticket_info = self._analyze_message(message_text)

            if should_create:
                self.logger.info(f"AI determined ticket should be created: {ticket_info.get('summary')}")

                # Get user info for better context
                user_info = client.users_info(user=user_id)
                user_name = user_info['user']['real_name']
                user_email = user_info['user'].get('profile', {}).get('email', 'unknown')

                # Create Jira ticket
                issue = self._create_jira_ticket(
                    ticket_info,
                    reporter_name=user_name,
                    reporter_email=user_email,
                    slack_channel=channel_name,
                    slack_message=message_text
                )

                # Send notification
                self._send_notification(
                    client=client,
                    issue_key=issue.key,
                    issue_url=f"{self.config['jira']['url']}/browse/{issue.key}",
                    original_message=message_text,
                    channel_name=channel_name,
                    user_id=user_id,
                    thread_ts=timestamp
                )

                self.logger.info(f"Successfully created ticket {issue.key}")
            else:
                self.logger.debug(f"AI determined no ticket needed for message: {message_text[:50]}...")

        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}", exc_info=True)

    def _analyze_message(self, message_text: str) -> Tuple[bool, Optional[Dict]]:
        """
        Use Claude AI to analyze if message should create a ticket.

        Returns:
            Tuple of (should_create_ticket, ticket_info_dict)
        """
        detection_mode = self.config['ai']['detection_mode']
        threshold = self.config['ai']['confidence_threshold']

        prompt = f"""Analyze the following Slack message and determine if it describes a bug report, task request, or issue that should be tracked in Jira.

Message: "{message_text}"

Detection mode: {detection_mode} (be {"generous and create tickets for anything that might need tracking" if detection_mode == "liberal" else "strict and only create tickets for clear bug reports or task requests"})

Please respond with a JSON object containing:
{{
    "should_create_ticket": true/false,
    "confidence": 0.0-1.0,
    "issue_type": "Bug" | "Task" | "Story" | "Improvement",
    "summary": "Brief one-line summary (max 100 chars)",
    "description": "Detailed description extracted from the message",
    "priority": "Highest" | "High" | "Medium" | "Low" | "Lowest",
    "reasoning": "Brief explanation of your decision"
}}

Guidelines:
- For bugs: Look for error messages, unexpected behavior, crashes, or things not working
- For tasks: Look for requests to implement features, make changes, or do work
- For improvements: Look for suggestions to enhance existing functionality
- Summary should be concise and actionable
- Description should include relevant details from the message
- Set appropriate priority based on urgency indicators in the message
- Confidence threshold is {threshold} - only create tickets if confidence is above this

Respond with ONLY the JSON object, no other text."""

        try:
            response = self.anthropic_client.messages.create(
                model=self.config['ai']['model'],
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Parse the response
            response_text = response.content[0].text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            result = json.loads(response_text)

            # Check confidence threshold
            should_create = (
                result.get('should_create_ticket', False) and
                result.get('confidence', 0) >= threshold
            )

            self.logger.debug(f"AI Analysis - Should create: {should_create}, Confidence: {result.get('confidence')}, Reasoning: {result.get('reasoning')}")

            if should_create:
                return True, {
                    'summary': result.get('summary'),
                    'description': result.get('description'),
                    'issue_type': result.get('issue_type', self.config['jira']['default_issue_type']),
                    'priority': result.get('priority', self.config['jira']['default_priority'])
                }
            else:
                return False, None

        except Exception as e:
            self.logger.error(f"Error in AI analysis: {str(e)}", exc_info=True)
            return False, None

    def _create_jira_ticket(
        self,
        ticket_info: Dict,
        reporter_name: str,
        reporter_email: str,
        slack_channel: str,
        slack_message: str
    ):
        """Create a Jira ticket with the extracted information."""

        # Build description with context
        description = f"""*Reported by:* {reporter_name} ({reporter_email})
*Slack Channel:* #{slack_channel}
*Original Message:*
{{quote}}
{slack_message}
{{quote}}

---

*AI-Generated Description:*
{ticket_info['description']}

---
_This ticket was automatically created by the Jira-Slack AI Agent on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_
"""

        # Create the issue
        issue_dict = {
            'project': {'key': self.config['jira']['project_key']},
            'summary': ticket_info['summary'],
            'description': description,
            'issuetype': {'name': ticket_info['issue_type']},
        }

        # Add priority if supported
        try:
            issue_dict['priority'] = {'name': ticket_info['priority']}
        except:
            pass  # Priority might not be available in all Jira configurations

        issue = self.jira_client.create_issue(fields=issue_dict)

        self.logger.info(f"Created Jira ticket {issue.key}: {ticket_info['summary']}")

        # Transition to desired initial status if configured
        desired_status = self.config['jira'].get('initial_status')
        if desired_status:
            self._set_issue_status(issue, desired_status)

        return issue

    def _set_issue_status(self, issue, desired_status: str):
        """
        Transition an issue to the desired status if it's not already there.

        Args:
            issue: The Jira issue object
            desired_status: The status name to transition to (e.g., "To Do")
        """
        try:
            # Refresh issue to get current status
            issue = self.jira_client.issue(issue.key)
            current_status = issue.fields.status.name

            if current_status == desired_status:
                self.logger.debug(f"Issue {issue.key} already in '{desired_status}' status")
                return

            # Get available transitions
            transitions = self.jira_client.transitions(issue)

            # Find the transition that leads to the desired status
            target_transition = None
            for transition in transitions:
                if transition['to']['name'] == desired_status:
                    target_transition = transition
                    break

            if target_transition:
                self.jira_client.transition_issue(issue, target_transition['id'])
                self.logger.info(f"Transitioned {issue.key} from '{current_status}' to '{desired_status}'")
            else:
                # Log available transitions for debugging
                available = [t['to']['name'] for t in transitions]
                self.logger.warning(
                    f"Cannot transition {issue.key} to '{desired_status}'. "
                    f"Current status: '{current_status}'. "
                    f"Available transitions: {', '.join(available)}"
                )

        except Exception as e:
            self.logger.error(f"Error setting status for {issue.key}: {str(e)}", exc_info=True)

    def _send_notification(
        self,
        client,
        issue_key: str,
        issue_url: str,
        original_message: str,
        channel_name: str,
        user_id: str,
        thread_ts: str
    ):
        """Send notification about the created ticket."""
        notification_channel = self.config['slack']['notification_channel']

        # Create a rich notification message
        message = f":white_check_mark: *Jira Ticket Created*\n\n" \
                  f"*Ticket:* <{issue_url}|{issue_key}>\n" \
                  f"*From:* <#{channel_name}> by <@{user_id}>\n" \
                  f"*Original Message:*\n```{original_message[:200]}{'...' if len(original_message) > 200 else ''}```"

        try:
            # Post to notification channel
            client.chat_postMessage(
                channel=notification_channel,
                text=message,
                unfurl_links=False
            )

            # Also reply in the original thread
            client.chat_postMessage(
                channel=channel_name,
                thread_ts=thread_ts,
                text=f":ticket: Created Jira ticket: <{issue_url}|{issue_key}>"
            )

            self.logger.info(f"Sent notification for {issue_key}")

        except Exception as e:
            self.logger.error(f"Error sending notification: {str(e)}", exc_info=True)

    def start(self):
        """Start the agent using Socket Mode."""
        app_token = os.getenv('SLACK_APP_TOKEN')

        if not app_token:
            raise ValueError(
                "SLACK_APP_TOKEN must be set in .env file. "
                "This is required for Socket Mode. "
                "Generate it in your Slack app settings under 'App-Level Tokens'."
            )

        self.logger.info("Starting Jira-Slack Agent in Socket Mode...")
        handler = SocketModeHandler(self.slack_app, app_token)
        handler.start()


def main():
    """Main entry point."""
    try:
        agent = JiraSlackAgent()
        agent.start()
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
