# Changelog

All notable changes to the Jira-Slack AI Agent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-20

### Added
- Initial release of Jira-Slack AI Agent
- Multi-channel Slack monitoring with configurable channels
- Claude AI-powered message analysis for bug/task detection
- Automatic Jira ticket creation with intelligent issue type detection
- Configurable detection sensitivity (liberal/conservative modes)
- Thread replies and dedicated channel notifications
- Rich ticket descriptions with Slack context and reporter information
- Comprehensive logging system
- Socket Mode support for Slack integration
- Environment-based configuration with .env file
- YAML-based agent configuration
- README with detailed setup instructions
- Example configuration files (.env.example, config.yaml.example)

### Features
- **AI Detection Modes**: Liberal and conservative detection options
- **Issue Type Detection**: Automatic classification as Bug, Task, Story, or Improvement
- **Priority Assignment**: AI-powered priority detection (Highest to Lowest)
- **Confidence Scoring**: Configurable threshold for ticket creation
- **Multi-Channel Support**: Monitor unlimited Slack channels simultaneously
- **Rich Notifications**: Post to both thread and notification channel
- **Status Management**: Optional initial status setting for new tickets

### Technical Details
- Python 3.7+ compatible
- Uses Claude Sonnet 4.5 for AI analysis
- Slack Bolt framework for event handling
- Jira API integration via jira-python library
- Anthropic API for Claude integration
