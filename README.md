# piglet

A CLI for managing PostHog resources - feature flags, cohorts, dashboards, insights, and projects.

> **Note:** This is not an official PostHog project. It is maintained by [Cased](https://cased.com).

## Installation

```bash
uv tool install cased-piglet
```

Or with pip:
```bash
pip install cased-piglet
```

## Configuration

Configuration can be provided via CLI options, environment variables, or config file (in that order of precedence).

### Environment Variables

```bash
export POSTHOG_API_KEY="phx_your_key"
export POSTHOG_PROJECT_ID="12345"
export POSTHOG_HOST="us"  # optional, defaults to us
```

### Config File

Create `~/.piglet/config.toml`:

```toml
api_key = "phx_your_key"
project_id = 12345
host = "us"
```

### Host Shortcuts

- `us` → `https://us.posthog.com` (default)
- `eu` → `https://eu.posthog.com`
- Or use a full URL for self-hosted: `https://posthog.mycompany.com`

## Global Options

```
--api-key TEXT        PostHog personal API key
--host TEXT           PostHog host (us, eu, or full URL)
--project-id INTEGER  PostHog project ID
--json                Output as JSON
--plain               Output as plain tab-separated text
```

## Commands

### Feature Flags

```bash
piglet flags list                # List all flags
piglet flags list --active       # List only active flags
piglet flags list --inactive     # List only inactive flags
piglet flags get <id-or-key>     # Get flag by ID or key
piglet flags create --key my-flag --name "My Flag" --rollout-percentage 50
piglet flags update 123 --rollout-percentage 100
piglet flags update 123 --active
piglet flags update 123 --inactive
piglet flags delete 123          # Prompts for confirmation
piglet flags delete 123 --yes    # Skip confirmation
```

### Cohorts

```bash
piglet cohorts list              # List all cohorts
piglet cohorts list --static     # List only static cohorts
piglet cohorts list --dynamic    # List only dynamic cohorts
piglet cohorts get 123           # Get cohort details
piglet cohorts create --name "My Cohort"
piglet cohorts create --name "Static Cohort" --static
piglet cohorts update 123 --name "New Name"
piglet cohorts delete 123
```

### Dashboards

```bash
piglet dashboards list           # List all dashboards
piglet dashboards list --pinned  # List only pinned dashboards
piglet dashboards get 123        # Get dashboard details
piglet dashboards create --name "My Dashboard"
piglet dashboards update 123 --name "New Name" --pinned
piglet dashboards delete 123
```

### Insights

```bash
piglet insights list             # List all insights
piglet insights list --saved     # List only saved insights
piglet insights list --favorited # List only favorited insights
piglet insights get <id-or-short-id>
piglet insights create --name "My Insight"
piglet insights update 123 --name "New Name"
piglet insights delete 123
```

### Projects

```bash
piglet projects list             # List all projects
piglet projects get 123          # Get project details
```

## Output Formats

```bash
# Rich table (default)
piglet flags list

# JSON output
piglet --json flags list

# Plain tab-separated (good for scripting)
piglet --plain flags list
piglet --plain flags list | cut -f2  # Extract just the keys
```

## Examples

```bash
# Use EU cloud
piglet --host eu flags list

# Self-hosted instance
piglet --host https://posthog.mycompany.com flags list

# Override project ID
piglet --project-id 99999 flags list

# Create and immediately enable a flag at 100%
piglet flags create --key new-feature --rollout-percentage 100 --active

# Disable a flag
piglet flags update 123 --inactive

# Export all flags as JSON
piglet --json flags list > flags.json
```

## Claude Code Plugin

A Claude Code plugin is available for natural language interaction with piglet:

```
/plugin marketplace add cased/claude-code-plugins
/plugin install piglet
```

Once installed, you can ask Claude things like:
- "What feature flags do we have?"
- "Create a flag called dark-mode with 50% rollout"
- "Disable the beta-feature flag"
- "List all cohorts"

## License

MIT

---

<p align="center">
  <img src="assets/piglet.png" alt="Piglet" width="300">
</p>
