# Weekly README Maintenance Workflow

This workflow automatically runs every Friday at 9:00 AM UTC to maintain the quality and relevance of the repository's README.md file.

## What it does

### 1. Link Verification
- Checks all links in the README.md file
- Verifies that links are accessible and return valid HTTP status codes
- Generates a report of any broken or inaccessible links

### 2. Project Discovery
- Searches GitHub for new blockchain greentech projects
- Looks for projects in categories matching existing content:
  - Energy Grid & P2P Trading
  - Digital Carbon Markets (ReFi)
  - Digital MRV (Measurement, Reporting, Verification)
  - Supply Chain & Circular Economy
  - Layer 1 Protocols (Green by Design)
- Filters results to find active projects (updated recently, with community traction)
- Excludes projects already listed in the README

### 3. Pull Request Creation
- If broken links or new projects are found, automatically creates a pull request
- The PR includes:
  - A report of broken links that need fixing
  - A list of newly discovered projects for review
  - All findings are presented for manual review before merging

## Manual Trigger

You can manually trigger this workflow at any time:
1. Go to the "Actions" tab in the GitHub repository
2. Select "Weekly README Maintenance"
3. Click "Run workflow"

## Configuration

The workflow is defined in `.github/workflows/weekly-readme-maintenance.yml`

### Scripts

Two Python scripts power this workflow:

- **`.github/scripts/check_links.py`**: Validates all HTTP/HTTPS links in README.md
- **`.github/scripts/search_projects.py`**: Searches GitHub for relevant new projects

### Customization

To modify search queries or categories, edit the `SEARCH_QUERIES` dictionary in `search_projects.py`.

To adjust link checking behavior (timeout, retries), modify the configuration constants in `check_links.py`.

## Requirements

- Python 3.11+
- Required Python packages: `requests`, `beautifulsoup4`, `markdown`
- GitHub token (automatically provided by GitHub Actions)

## Permissions

The workflow requires the following permissions:
- `contents: write` - To create branches and commits
- `pull-requests: write` - To create pull requests
- `issues: write` - To comment on issues if needed

## Notes

- The workflow uses rate limiting and respectful crawling practices
- All discovered projects should be manually reviewed before adding to README
- Link checks may report false positives for sites with aggressive bot protection
- The workflow will not automatically merge changes - human review is always required
