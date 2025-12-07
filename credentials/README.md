# Credentials Directory

This directory stores sensitive credentials for external services.

## Required Files

### Google Sheets API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API
4. Create a service account
5. Download the JSON credentials file
6. Save it as `google_credentials.json` in this directory

## Security

⚠️ **IMPORTANT**: Never commit credentials to version control!

This directory is already included in `.gitignore`.
