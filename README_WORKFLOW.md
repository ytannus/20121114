# Email Attachments to Dropbox - n8n Workflow

## Overview

This n8n workflow automatically extracts attachments from incoming emails and organizes them in Dropbox folders by sender email address.

## Features

✅ **Automatic Email Processing** - Monitors INBOX for new emails
✅ **Sender-Based Organization** - Creates folders named by sender email
✅ **Multiple Attachments** - Handles multiple files per email
✅ **Smart Filtering** - Only processes emails with attachments
✅ **Error Handling** - Continues even if folder already exists
✅ **Detailed Tracking** - Logs file name, size, sender, and date

## Quick Start

### 1. Import Workflow
- Open n8n → Import from File
- Select `n8n-email-to-dropbox-fixed.json`

### 2. Configure Credentials
- **Email (IMAP)**: Add your email credentials
- **Dropbox**: Add Dropbox access token or OAuth2

### 3. Activate
- Save workflow
- Toggle Active ON

**See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed setup instructions.**

## How It Works

```
Email Arrives → Has Attachments? → Extract Sender Info
                      ↓                      ↓
                  Skip Email          Create Folder
                                            ↓
                                    Split Attachments
                                            ↓
                                    Upload to Dropbox
                                            ↓
                                     Track Success
```

## Folder Structure

```
/Emails/
  ├── john.doe@example.com/
  │   ├── invoice.pdf
  │   └── photo.jpg
  ├── jane@company.com/
  │   └── report.xlsx
  └── support@service.com/
      └── ticket.pdf
```

## Files

- **n8n-email-to-dropbox-fixed.json** - n8n workflow file
- **SETUP_GUIDE.md** - Complete setup instructions
- **N8N_WORKFLOWS_README.md** - Detailed documentation

## Requirements

- n8n instance (self-hosted or cloud)
- Email account with IMAP access
- Dropbox account with API access

## IMAP Settings

| Provider | Host | Port |
|----------|------|------|
| Gmail | imap.gmail.com | 993 |
| Outlook | outlook.office365.com | 993 |
| Yahoo | imap.mail.yahoo.com | 993 |

## Customization

**Change base folder:**
Edit path in "Create Sender Folder" and "Upload to Dropbox" nodes.

**Add date subfolders:**
Use: `/Emails/{{ $json.senderFolder }}/{{ $now.format('yyyy-MM') }}/{{ $json.filename }}`

**Filter by file type:**
Add IF node with: `{{ $json.contentType.includes('pdf') }}`

## Troubleshooting

**Workflow not triggering:**
- Check workflow is Active
- Verify IMAP credentials
- Check email polling interval

**Dropbox errors:**
- Verify access token is valid
- Check app permissions
- Ensure sufficient storage

**See [SETUP_GUIDE.md](SETUP_GUIDE.md) for more solutions.**

## Support

Check n8n execution logs for detailed error messages.

---

**Ready to use - just configure credentials and activate!** 🚀
