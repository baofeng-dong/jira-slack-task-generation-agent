# Publishing Guide

This guide walks you through publishing your Jira-Slack AI Agent to GitHub and Docker Hub.

## ✅ What's Already Done

All publishing files have been created and committed:
- ✅ LICENSE (MIT)
- ✅ CONTRIBUTING.md (contributor guidelines)
- ✅ CHANGELOG.md (version history)
- ✅ Dockerfile (optimized container build)
- ✅ docker-compose.yml (easy deployment)
- ✅ DOCKER.md (comprehensive Docker guide)
- ✅ README.md (updated with badges and Docker instructions)
- ✅ All files committed to git

## Step 1: Push to GitHub

1. **Push your changes to GitHub:**
   ```bash
   git push origin main
   ```

2. **Make the repository public** (if it's currently private):
   - Go to your repository on GitHub
   - Click **Settings** (top right)
   - Scroll to bottom → **Danger Zone**
   - Click **Change visibility** → **Make public**
   - Confirm by typing the repository name

3. **Update repository details:**
   - Go to your repository main page
   - Click the ⚙️ icon next to "About" (top right)
   - Add:
     - **Description**: "AI-powered agent that monitors Slack channels and automatically creates Jira tickets using Claude AI"
     - **Website**: Your documentation site (optional)
     - **Topics**: `slack`, `jira`, `ai`, `claude`, `automation`, `python`, `docker`, `ticket-management`, `bug-tracking`
   - ✅ Check "Releases" and "Packages"
   - Click **Save changes**

4. **Update URLs in documentation:**
   - Find and replace `baofeng-dong` with your GitHub username in:
     - README.md (lines 16, 481-482)
     - DOCKER.md (multiple locations)
     - CONTRIBUTING.md (line 18)

   ```bash
   # Quick find/replace (update YOUR_GITHUB_USERNAME first)
   sed -i '' 's/baofeng-dong/YOUR_GITHUB_USERNAME/g' README.md DOCKER.md CONTRIBUTING.md
   git add README.md DOCKER.md CONTRIBUTING.md
   git commit -m "Update: Replace placeholder GitHub username"
   git push
   ```

## Step 2: Test Docker Build Locally

Before publishing to Docker Hub, test the build locally:

1. **Build the Docker image:**
   ```bash
   docker build -t jira-slack-agent:test .
   ```

2. **Test the image:**
   ```bash
   # Create test environment file
   cp .env.example .env.test
   # Edit .env.test with valid credentials

   # Run the container
   docker run --rm \
     --env-file .env.test \
     -v $(pwd)/config.yaml:/app/config.yaml:ro \
     jira-slack-agent:test
   ```

3. **Verify it works:**
   - Check that the agent starts without errors
   - Post a test message in Slack
   - Verify a Jira ticket is created
   - Stop with Ctrl+C

4. **Test with Docker Compose:**
   ```bash
   docker-compose up
   # Verify it works, then stop with Ctrl+C
   docker-compose down
   ```

## Step 3: Publish to Docker Hub

1. **Create Docker Hub account** (if you don't have one):
   - Go to https://hub.docker.com/signup
   - Create a free account
   - Verify your email

2. **Login to Docker Hub:**
   ```bash
   docker login
   # Enter your Docker Hub username and password
   ```

3. **Tag your image:**
   ```bash
   # Replace YOUR_DOCKERHUB_USERNAME with your actual username
   docker tag jira-slack-agent:test YOUR_DOCKERHUB_USERNAME/jira-slack-agent:latest
   docker tag jira-slack-agent:test YOUR_DOCKERHUB_USERNAME/jira-slack-agent:1.0.0
   ```

4. **Push to Docker Hub:**
   ```bash
   docker push YOUR_DOCKERHUB_USERNAME/jira-slack-agent:latest
   docker push YOUR_DOCKERHUB_USERNAME/jira-slack-agent:1.0.0
   ```

5. **Update Docker Hub repository:**
   - Go to https://hub.docker.com/r/YOUR_DOCKERHUB_USERNAME/jira-slack-agent
   - Click **Edit** on the overview
   - Add a description and README
   - Link to your GitHub repository

6. **Update documentation with Docker Hub image:**
   ```bash
   # Update DOCKER.md and docker-compose.yml with your Docker Hub username
   # In DOCKER.md, replace YOUR_DOCKERHUB_USERNAME with your actual username
   # In docker-compose.yml, uncomment the image line and update username

   git add DOCKER.md docker-compose.yml
   git commit -m "Update: Add Docker Hub image references"
   git push
   ```

## Step 4: Build Multi-Platform Images (Optional)

To support both Intel/AMD and ARM (Apple Silicon, Raspberry Pi):

1. **Set up buildx:**
   ```bash
   docker buildx create --name multiplatform --use
   docker buildx inspect --bootstrap
   ```

2. **Build and push multi-platform image:**
   ```bash
   docker buildx build \
     --platform linux/amd64,linux/arm64 \
     -t YOUR_DOCKERHUB_USERNAME/jira-slack-agent:latest \
     -t YOUR_DOCKERHUB_USERNAME/jira-slack-agent:1.0.0 \
     --push \
     .
   ```

## Step 5: Create GitHub Release

1. **Create a release on GitHub:**
   - Go to your repository
   - Click **Releases** (right sidebar)
   - Click **Create a new release**
   - Tag version: `v1.0.0`
   - Release title: `v1.0.0 - Initial Release`
   - Description: Copy from CHANGELOG.md
   - Click **Publish release**

2. **Add release badge to README:**
   ```markdown
   [![Release](https://img.shields.io/github/v/release/baofeng-dong/jira-slack-task-generation-agent)](https://github.com/baofeng-dong/jira-slack-task-generation-agent/releases)
   ```

## Step 6: Promote Your Agent

1. **Share on social media:**
   - Twitter/X: Share with #AI #Slack #Jira hashtags
   - LinkedIn: Post about your automation project
   - Reddit: r/programming, r/slack, r/jira

2. **Submit to directories:**
   - [Awesome Slack](https://github.com/matiassingers/awesome-slack)
   - [Awesome Jira](https://github.com/rodolfobandeira/awesome-jira)
   - [Made with Claude](https://www.madewitclaude.com/)

3. **Write a blog post:**
   - How you built it
   - Problems it solves
   - Technical decisions
   - Results and metrics

## Maintenance

1. **Keep dependencies updated:**
   ```bash
   pip list --outdated
   pip install --upgrade <package>
   # Test thoroughly after updates
   ```

2. **Update CHANGELOG.md** for each release

3. **Respond to GitHub issues** and pull requests

4. **Security:**
   - Enable Dependabot alerts in GitHub settings
   - Monitor for security vulnerabilities
   - Rotate API keys periodically

## Quick Reference Commands

```bash
# Local testing
docker build -t jira-slack-agent:test .
docker-compose up

# Publishing to Docker Hub
docker login
docker tag jira-slack-agent:test YOUR_DOCKERHUB_USERNAME/jira-slack-agent:latest
docker push YOUR_DOCKERHUB_USERNAME/jira-slack-agent:latest

# Push to GitHub
git push origin main

# Create release
# Do this via GitHub UI: Releases → Create new release
```

## Support

If you have questions about publishing:
- Check Docker Hub documentation: https://docs.docker.com/docker-hub/
- Check GitHub documentation: https://docs.github.com/
- Open an issue if you find problems with this guide

## Congratulations! 🎉

Your agent is now published and ready for others to use!

Users can deploy it with just:
```bash
git clone https://github.com/baofeng-dong/jira-slack-task-generation-agent.git
cd jira-slack-agent
cp .env.example .env
cp config.yaml.example config.yaml
# Edit .env and config.yaml
docker-compose up -d
```

Or using your Docker Hub image:
```bash
docker pull YOUR_DOCKERHUB_USERNAME/jira-slack-agent:latest
docker run -d --env-file .env -v ./config.yaml:/app/config.yaml YOUR_DOCKERHUB_USERNAME/jira-slack-agent:latest
```
