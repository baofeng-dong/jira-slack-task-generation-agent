# Contributing to Jira-Slack AI Agent

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS, etc.)
- Relevant log excerpts

### Suggesting Enhancements

Enhancement suggestions are welcome! Please open an issue with:
- Clear description of the proposed feature
- Use case and benefits
- Any implementation ideas (optional)

### Pull Requests

1. **Fork the repository** and create a new branch
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation if needed

3. **Test your changes**
   - Ensure the agent runs without errors
   - Test with sample Slack messages
   - Verify Jira tickets are created correctly

4. **Commit your changes**
   ```bash
   git commit -m "Add: Brief description of your change"
   ```
   Use conventional commit prefixes:
   - `Add:` for new features
   - `Fix:` for bug fixes
   - `Update:` for improvements
   - `Docs:` for documentation changes

5. **Push and create a Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Development Setup

1. Clone the repository
   ```bash
   git clone https://github.com/baofeng-dong/jira-slack-task-generation-agent.git
   cd jira-slack-agent
   ```

2. Create virtual environment
   ```bash
   python3 -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment
   ```bash
   cp .env.example .env
   # Edit .env with your API credentials
   cp config.yaml.example config.yaml
   # Edit config.yaml with your settings
   ```

## Code Style

- Follow PEP 8 Python style guide
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and modular

## Testing

Before submitting a PR:
- Test the agent with various message types
- Verify error handling works correctly
- Check logs for any warnings or errors
- Test with both liberal and conservative detection modes

## Questions?

Feel free to open an issue for any questions about contributing!
