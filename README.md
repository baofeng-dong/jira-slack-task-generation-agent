# Jira-Slack AI Agent

An intelligent agent that monitors Slack channels for bug reports and task requests, uses Claude AI to detect and classify them, then automatically creates Jira tickets and sends notifications.

## Features

- **Multi-channel monitoring** - Monitor multiple Slack channels simultaneously (fully configurable)
- **AI-powered message analysis** - Uses Claude API to intelligently detect bugs and tasks
- **Automatic Jira ticket creation** - Creates tickets with intelligent issue type detection
- **Configurable detection sensitivity** - Liberal or conservative modes
- **Thread replies and channel notifications** - Notifies in both thread and dedicated channel
- **Rich ticket descriptions** - Includes Slack message context and reporter information
- **Comprehensive logging** - Track all operations and decisions

## Architecture

```
Slack Message → Claude AI Analysis → Jira Ticket Creation → Slack Notification
```

## Prerequisites

- Python 3.7 or higher
- A Slack workspace where you can create apps
- Jira access with ticket creation permissions
- Anthropic API access

## Setup Instructions

### 1. Clone and Install Dependencies

```bash
cd jira-slack-agent
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Create Slack App

1. Go to https://api.slack.com/apps
2. Click **"Create New App"** → **"From scratch"**
3. Enter app name (e.g., "Jira Ticket Bot") and select your workspace
4. Click **"Create App"**

#### 2.1 Configure OAuth & Permissions

1. In the left sidebar, click **"OAuth & Permissions"**
2. Scroll to **"Scopes"** → **"Bot Token Scopes"**
3. Add the following scopes:
   - `channels:history` - Read messages from public channels
   - `channels:read` - View basic channel info
   - `chat:write` - Send messages
   - `users:read` - View user information
   - `users:read.email` - View email addresses

4. Scroll to top and click **"Install to Workspace"**
5. Authorize the app
6. Copy the **"Bot User OAuth Token"** (starts with `xoxb-`)
   - Save this as `SLACK_BOT_TOKEN` in your `.env` file

#### 2.2 Enable Socket Mode

1. In the left sidebar, click **"Socket Mode"**
2. Toggle **"Enable Socket Mode"** to ON
3. Give the token a name (e.g., "jira-agent-socket")
4. Click **"Generate"**
5. Copy the **App-Level Token** (starts with `xapp-`)
   - Save this as `SLACK_APP_TOKEN` in your `.env` file

#### 2.3 Enable Events

1. In the left sidebar, click **"Event Subscriptions"**
2. Toggle **"Enable Events"** to ON
3. Under **"Subscribe to bot events"**, add:
   - `message.channels` - Messages in public channels
4. Click **"Save Changes"**

#### 2.4 Add Bot to Channels

After configuring which channels to monitor in `config.yaml` (see step 5.2), you need to invite the bot to those channels in Slack:

1. In Slack, go to each channel you want to monitor (e.g., `#engineering`)
2. Type `/invite @Jira Ticket Bot` (or your app name)
3. Repeat for **every channel** listed in your `monitored_channels` config
4. Also invite the bot to your `notification_channel` (default: `#bug-task-notifications`)

**Note:** The bot can only monitor channels it has been invited to, even if they're listed in the config.

#### 2.5 Get Signing Secret

1. In the left sidebar, click **"Basic Information"**
2. Scroll to **"App Credentials"**
3. Copy the **"Signing Secret"**
   - Save this as `SLACK_SIGNING_SECRET` in your `.env` file

### 3. Get Jira API Token

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **"Create API token"**
3. Give it a label (e.g., "Jira Slack Agent")
4. Click **"Create"**
5. Copy the token (you won't be able to see it again!)
   - Save this as `JIRA_API_TOKEN` in your `.env` file
6. Also note your Atlassian account email
   - Save this as `JIRA_EMAIL` in your `.env` file

### 4. Get Claude API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in to your account
3. Go to **"API Keys"** in settings: https://console.anthropic.com/settings/keys
4. Click **"Create Key"**
5. Give it a name (e.g., "Jira Slack Agent")
6. Copy the API key (starts with `sk-ant-`)
   - Save this as `ANTHROPIC_API_KEY` in your `.env` file

### 5. Configure the Agent

#### 5.1 Set Up API Credentials

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and fill in all the API keys and credentials you collected:
```bash
# Example .env file
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
SLACK_SIGNING_SECRET=your-signing-secret-here
JIRA_EMAIL=your.email@example.com
JIRA_API_TOKEN=your-jira-api-token-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

#### 5.2 Configure Monitored Channels (IMPORTANT)

Edit `config.yaml` to specify which Slack channels to monitor:

```yaml
slack:
  # Channels to monitor for bugs/tasks (without the # symbol)
  monitored_channels:
    - "engineering"       # Default channel
    - "engineering"             # Add more channels as needed
    - "support-requests"
    - "bug-reports"

  # Channel to post notifications when tickets are created
  notification_channel: "bug-task-notifications"
```

**Important Notes:**
- ✅ Use channel names **without the # symbol** (e.g., `"engineering"` not `"#engineering"`)
- ✅ You can monitor as many channels as you want
- ✅ **Don't forget to invite the bot** to each channel in Slack using `/invite @YourBotName`
- ✅ Changes take effect after restarting the agent

#### 5.3 Optional: Adjust AI Detection Settings

You can customize the detection behavior in `config.yaml`:

```yaml
ai:
  # "liberal" = create tickets generously, "conservative" = only when very confident
  detection_mode: "liberal"

  # Confidence threshold (0.0 to 1.0)
  # Liberal mode: 0.3-0.5, Conservative mode: 0.7-0.9
  confidence_threshold: 0.4
```

## Running the Agent

### Start the Agent

```bash
source venv/bin/activate  # If not already activated
python agent.py
```

You should see output like:
```
2025-11-28 10:00:00 - __main__ - INFO - Slack app initialized
2025-11-28 10:00:00 - __main__ - INFO - Jira client initialized for https://your-instance.atlassian.net
2025-11-28 10:00:00 - __main__ - INFO - Anthropic client initialized
2025-11-28 10:00:00 - __main__ - INFO - Jira-Slack Agent initialized successfully
2025-11-28 10:00:00 - __main__ - INFO - Starting Jira-Slack Agent in Socket Mode...
⚡️ Bolt app is running!
```

### Running as a Background Service

To keep the agent running continuously on your local server:

#### Using screen (Linux/Mac)

```bash
screen -S jira-agent
source venv/bin/activate
python agent.py

# Press Ctrl+A then D to detach
# To reattach: screen -r jira-agent
```

#### Using nohup (Linux/Mac)

```bash
nohup python agent.py > output.log 2>&1 &
```

#### Using systemd (Linux)

Create `/etc/systemd/system/jira-slack-agent.service`:

```ini
[Unit]
Description=Jira Slack AI Agent
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/jira-slack-agent
Environment=PATH=/path/to/jira-slack-agent/venv/bin
ExecStart=/path/to/jira-slack-agent/venv/bin/python agent.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable jira-slack-agent
sudo systemctl start jira-slack-agent
sudo systemctl status jira-slack-agent
```

## Testing

1. Make sure the bot is invited to your monitored channel(s)
   ```
   /invite @Jira Ticket Bot
   ```

2. Go to one of your monitored channels (e.g., `#engineering`) in Slack

3. Post a test message like:
   ```
   Hey team, I'm seeing an error when trying to switch clients.
   The page throws a 500 error and nothing happens. Can someone look into this?
   ```

4. Watch the agent logs - you should see:
   - Message received and analyzed by Claude
   - AI decision and confidence score
   - Jira ticket created
   - Notification posted to `#bug-task-notifications`
   - Reply in the original thread with ticket link

5. Try different message types to test the AI detection:
   - Bug: "Getting a null pointer exception on login"
   - Task: "We need to add validation to the email field"
   - Feature: "Can we implement dark mode?"

## Configuration Options

### Detection Mode

In `config.yaml`, you can adjust the detection sensitivity:

```yaml
ai:
  detection_mode: "liberal"  # or "conservative"
  confidence_threshold: 0.4   # 0.0 to 1.0
```

- **Liberal mode** (threshold: 0.3-0.5): Creates tickets for anything that might need tracking
- **Conservative mode** (threshold: 0.7-0.9): Only creates tickets for clear bug reports or tasks

### Issue Type Detection

The AI automatically determines issue types:
- **Bug**: Error messages, crashes, unexpected behavior
- **Task**: Requests to implement features or make changes
- **Story**: User stories or larger feature requests
- **Improvement**: Suggestions to enhance existing functionality

### Monitored Channels Configuration

The agent can monitor **multiple Slack channels simultaneously**. All configuration is done in `config.yaml`:

#### Adding Channels

```yaml
slack:
  monitored_channels:
    - "engineering"
    - "support-requests"
    - "support-requests"
    - "bug-reports"
    - "platform-team"
```

#### Changing Channels

Simply edit the list and restart the agent:

```yaml
slack:
  monitored_channels:
    - "new-channel-name"      # Replace with your channel
```

#### Important Rules

1. **No # symbol** - Use `"engineering"` not `"#engineering"`
2. **Invite the bot** - After adding a channel to config, invite the bot in Slack:
   ```
   /invite @Jira Ticket Bot
   ```
3. **Restart required** - After changing `config.yaml`, restart the agent for changes to take effect
4. **Monitor notification channel** - The bot must also be in the `notification_channel`

#### Examples

Monitor a single channel:
```yaml
monitored_channels:
  - "incidents"
```

Monitor multiple teams:
```yaml
monitored_channels:
  - "backend-team"
  - "frontend-team"
  - "mobile-team"
```

Monitor support and engineering:
```yaml
monitored_channels:
  - "customer-support"
  - "engineering-bugs"
  - "feature-requests"
```

## Logging

Logs are written to:
- `agent.log` file (configurable in `config.yaml`)
- Console output

Log levels: DEBUG, INFO, WARNING, ERROR

Change log level in `config.yaml`:
```yaml
logging:
  level: "DEBUG"  # For more verbose output
```

## Troubleshooting

### "SLACK_BOT_TOKEN must be set"
- Make sure `.env` file exists and contains valid tokens
- Check that you've run `cp .env.example .env`

### "SLACK_APP_TOKEN must be set"
- Enable Socket Mode in your Slack app settings
- Generate an App-Level Token

### "Error: channel_not_found"
- Make sure the bot is invited to the monitored channels
- Use `/invite @BotName` in each channel

### "Jira authentication failed"
- Verify your Jira email and API token are correct
- Test the token at https://id.atlassian.com/manage-profile/security/api-tokens

### "Anthropic API error"
- Check your API key is valid
- Verify you have API credits available at https://console.anthropic.com/

### Messages not being processed
- **Check the bot is invited:** Use `/invite @BotName` in the channel
- **Verify channel names:** In `config.yaml`, use channel names WITHOUT the # symbol
  - ✅ Correct: `"engineering"`
  - ❌ Wrong: `"#engineering"`
- **Check exact spelling:** Channel names in config must match Slack exactly
- **Restart the agent:** After changing `config.yaml`, restart is required
- **Check logs:** `tail -f agent.log` to see if messages are being received
- **Verify monitored_channels list:** Ensure the channel is in the config list

### Bot not starting
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Activate virtual environment: `source venv/bin/activate`
- Check Python version: `python --version` (need 3.7+)

## Project Structure

```
jira-slack-agent/
├── agent.py              # Main agent code
├── config.yaml           # Configuration file
├── .env                  # Environment variables (not in git)
├── .env.example          # Template for .env
├── requirements.txt      # Python dependencies
├── README.md             # This file
└── agent.log             # Log file (created at runtime)
```

## Security Notes

- Never commit `.env` file to version control
- Rotate API keys periodically
- Use restrictive Slack OAuth scopes
- Monitor agent logs for suspicious activity
- Consider using a dedicated Jira service account

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review logs in `agent.log`
3. Verify all API credentials are correct
4. Test each integration individually (Slack, Jira, Claude)

## License

MIT License - Feel free to use and modify for your own purposes.
