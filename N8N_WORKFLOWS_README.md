# n8n Email Attachments to Dropbox Workflows

## Overview

These n8n workflows automatically extract attachments from incoming emails and organize them in Dropbox folders based on the sender's email address. Two versions are provided:

1. **IMAP Version** - Works with any email service supporting IMAP
2. **Gmail Version** - Optimized for Gmail with OAuth2 authentication

## Features

✅ **Automatic Email Monitoring** - Triggers when new emails arrive
✅ **Sender-Based Organization** - Creates folders named after sender email addresses
✅ **Multiple Attachments** - Handles emails with multiple attachments
✅ **Smart Filtering** - Only processes emails with attachments
✅ **Error Handling** - Continues on folder creation errors (if folder exists)
✅ **Detailed Logging** - Tracks file name, size, sender, and upload date
✅ **Auto-Marking** - Marks processed emails (Gmail version)

## Workflow Comparison

| Feature | IMAP Version | Gmail Version |
|---------|-------------|---------------|
| Email Service | Any IMAP server | Gmail only |
| Authentication | Username/Password | OAuth2 |
| Email Marking | Mark as Read | Add Label |
| Real-time | Polls periodically | Webhook (instant) |
| Setup Complexity | Simple | Medium |
| Security | Basic Auth | OAuth2 (more secure) |

## Folder Structure in Dropbox

```
📁 Dropbox
└── 📁 Emails
    ├── 📁 john.doe@example.com
    │   ├── 📄 invoice_2024.pdf
    │   ├── 📄 contract.docx
    │   └── 📄 photo.jpg
    ├── 📁 jane_smith@company_com
    │   ├── 📄 presentation.pptx
    │   └── 📄 report.xlsx
    └── 📁 support@service_com
        └── 📄 ticket_response.pdf
```

**Note**: Special characters in email addresses are replaced with underscores for folder names.

## Installation & Setup

### Prerequisites

1. **n8n instance** (self-hosted or cloud)
2. **Email account** (IMAP access or Gmail)
3. **Dropbox account** with API access

### Step 1: Set Up Credentials

#### For IMAP Version

1. In n8n, go to **Credentials** → **Create New Credential**
2. Select **IMAP**
3. Fill in:
   - **User**: your email address
   - **Password**: your email password or app-specific password
   - **Host**: IMAP server (e.g., imap.gmail.com, outlook.office365.com)
   - **Port**: 993 (SSL) or 143 (TLS)
   - **Security**: SSL/TLS
4. Click **Save**

**Common IMAP Settings:**
- **Gmail**: imap.gmail.com:993 (SSL)
- **Outlook**: outlook.office365.com:993 (SSL)
- **Yahoo**: imap.mail.yahoo.com:993 (SSL)
- **iCloud**: imap.mail.me.com:993 (SSL)

#### For Gmail Version

1. In n8n, go to **Credentials** → **Create New Credential**
2. Select **Gmail OAuth2 API**
3. Follow the OAuth2 setup wizard:
   - Create Google Cloud Project
   - Enable Gmail API
   - Create OAuth2 credentials
   - Add authorized redirect URI: `https://your-n8n-instance/rest/oauth2-credential/callback`
4. Authorize access
5. Click **Save**

#### Dropbox Setup (Both Versions)

1. In n8n, go to **Credentials** → **Create New Credential**
2. Select **Dropbox API**
3. Two options:

   **Option A: OAuth2 (Recommended)**
   - Create Dropbox App at https://www.dropbox.com/developers/apps
   - Select "Scoped access"
   - Select "Full Dropbox"
   - Set redirect URI: `https://your-n8n-instance/rest/oauth2-credential/callback`
   - Copy App Key and App Secret
   - Authorize access in n8n

   **Option B: Access Token**
   - Create Dropbox App
   - Generate Access Token in app settings
   - Paste token in n8n
4. Click **Save**

### Step 2: Import Workflow

1. Copy the JSON content from either:
   - `n8n-email-attachments-to-dropbox.json` (IMAP)
   - `n8n-gmail-attachments-to-dropbox.json` (Gmail)

2. In n8n, click **Import from File** or **Import from URL**

3. Paste the JSON content

4. Click **Import**

### Step 3: Configure Workflow

1. Open the imported workflow

2. **Update Credentials**:
   - Click on "Email Trigger (IMAP)" or "Gmail Trigger" node
   - Select your email credential from dropdown
   - Click on "Create Dropbox Folder" node
   - Select your Dropbox credential
   - Click on "Upload to Dropbox" node
   - Select same Dropbox credential

3. **Customize Settings** (Optional):
   - **Mailbox**: Change from "INBOX" if needed
   - **Post Process Action**: Keep "markAsRead" or change to "nothing"
   - **Base Folder**: Edit folder path in "Create Dropbox Folder" node
     - Default: `/Emails/`
     - Can change to any path like `/Attachments/`, `/Documents/`, etc.

4. **Save** the workflow

5. **Activate** the workflow (toggle switch in top right)

## Workflow Explanation

### Node Breakdown

#### 1. Email Trigger / Gmail Trigger
- **Purpose**: Monitors inbox for new emails
- **Triggers**: When new email arrives
- **Output**: Email data including sender, subject, date, attachments

#### 2. Has Attachments?
- **Purpose**: Filter emails with attachments
- **Logic**: Checks if `attachments` field is not empty
- **Branches**:
  - TRUE → Process attachments
  - FALSE → Skip (No Operation)

#### 3. Extract Sender Info
- **Purpose**: Parse sender information
- **Extracts**:
  - Sender email address
  - Sender name (or email username if name not available)
  - Email subject
  - Received date
  - Folder name (email with special chars replaced)
- **Output**: Structured sender data

#### 4. Create Dropbox Folder
- **Purpose**: Create sender-specific folder in Dropbox
- **Path**: `/Emails/{sender_email}`
- **Error Handling**: Continues on fail (if folder exists)
- **Output**: Folder path

#### 5. Set Folder Path
- **Purpose**: Store folder path for later use
- **Data**:
  - Full folder path
  - Sender information
  - Email subject
- **Output**: Ready for attachment processing

#### 6. Split Attachments
- **Purpose**: Convert attachment array to individual items
- **Logic**: Splits `attachments` field
- **Output**: One item per attachment

#### 7. Upload to Dropbox
- **Purpose**: Upload each attachment to Dropbox
- **Path**: `/Emails/{sender_email}/{filename}`
- **Mode**: Overwrite (if file exists)
- **Output**: Dropbox file metadata

#### 8. Format Output
- **Purpose**: Create summary of uploaded file
- **Data**:
  - File name and size
  - Sender email and subject
  - Dropbox path
  - Upload timestamp
- **Output**: Formatted summary

#### 9. Mark Email as Processed (Gmail only)
- **Purpose**: Add label to processed emails
- **Action**: Adds "Processed" label
- **Error Handling**: Continues on fail

## Customization Options

### Change Base Folder

Edit the "Create Dropbox Folder" node:

```javascript
// From:
path: "={{ '/Emails/' + $json.folderName }}"

// To:
path: "={{ '/Attachments/' + $json.folderName }}"
// or
path: "={{ '/Documents/' + $json.folderName }}"
```

### Use Sender Name Instead of Email

Edit "Extract Sender Info" node, change `folderName`:

```javascript
// From:
"folderName": "={{ $json.from.address.replace(/[^a-zA-Z0-9@._-]/g, '_') }}"

// To use sender name:
"folderName": "={{ ($json.from.name || $json.from.address).replace(/[^a-zA-Z0-9@._-]/g, '_') }}"
```

### Add Date-Based Subfolders

Edit "Upload to Dropbox" node:

```javascript
// From:
path: "={{ $('Set Folder Path').item.json.folderPath + '/' + $json.filename }}"

// To add date subfolder:
path: "={{ $('Set Folder Path').item.json.folderPath + '/' + $now.format('yyyy-MM') + '/' + $json.filename }}"
```

This creates: `/Emails/sender@email.com/2025-11/file.pdf`

### Filter by File Type

Add an "IF" node after "Split Attachments":

```javascript
// Condition:
{{ $json.contentType.includes('pdf') || $json.contentType.includes('image') }}
```

This only processes PDFs and images.

### Add File Size Limit

Add an "IF" node after "Split Attachments":

```javascript
// Condition (max 10MB):
{{ $json.size < 10485760 }}
```

### Send Notification Email

Add an "Email" node after "Format Output":

```javascript
// To: your-email@example.com
// Subject: "New Attachment from {{ $json.senderEmail }}"
// Body:
File: {{ $json.fileName }}
From: {{ $json.senderEmail }}
Subject: {{ $json.emailSubject }}
Uploaded to: {{ $json.uploadedFile }}
```

### Organize by Domain

Edit "Extract Sender Info" node:

```javascript
"folderName": "={{ $json.from.address.split('@')[1].replace(/[^a-zA-Z0-9._-]/g, '_') }}"
```

This groups all emails from same domain (e.g., all @company.com together).

## Troubleshooting

### Issue: Workflow not triggering

**IMAP Version:**
- Check IMAP credentials are valid
- Verify IMAP access is enabled on email account
- Check n8n has network access to IMAP server
- Ensure workflow is activated (toggle switch ON)
- Check polling interval (default: 5 minutes)

**Gmail Version:**
- Verify Gmail API is enabled in Google Cloud Console
- Check OAuth2 token hasn't expired
- Ensure webhook URL is accessible
- Check Gmail API quotas

### Issue: "Folder already exists" error

**Solution**: This is normal and handled! The workflow has `continueOnFail: true` on folder creation, so it proceeds even if folder exists.

### Issue: Attachments not uploading

**Check:**
- Dropbox credential is valid
- Dropbox has sufficient storage space
- File names don't contain invalid characters
- Network connectivity to Dropbox API

**Debug:**
- Check execution logs in n8n
- Look at "Split Attachments" node output
- Verify binary data is present

### Issue: Special characters in filenames

**Solution**: Add a node to sanitize filenames before upload:

```javascript
"sanitizedFilename": "={{ $json.filename.replace(/[^a-zA-Z0-9._-]/g, '_') }}"
```

### Issue: Large attachments failing

**Solutions:**
1. Increase n8n execution timeout
2. Add file size filtering
3. Upgrade Dropbox plan for more space
4. Use Dropbox API v2 upload sessions for files >150MB

### Issue: Duplicate uploads

**IMAP Version:**
- Change `postProcessAction` to "delete" instead of "markAsRead"
- Or use "move" to move processed emails to another folder

**Gmail Version:**
- Check if "Processed" label is being applied
- Add a filter at start to exclude already processed emails

## Advanced Configurations

### Multi-Account Setup

Run separate workflows for each email account:
1. Duplicate the workflow
2. Rename (e.g., "Email Attachments - Account 1")
3. Use different credentials
4. Optionally use different base folders

### Webhook Integration

Add a Webhook node after "Format Output" to notify other systems:

```javascript
{
  "event": "attachment_uploaded",
  "file": "{{ $json.fileName }}",
  "from": "{{ $json.senderEmail }}",
  "path": "{{ $json.uploadedFile }}",
  "timestamp": "{{ $json.uploadDate }}"
}
```

### Database Logging

Add a PostgreSQL/MySQL node after "Format Output" to log uploads:

```sql
INSERT INTO email_attachments
  (file_name, sender_email, email_subject, dropbox_path, upload_date)
VALUES
  ('{{ $json.fileName }}', '{{ $json.senderEmail }}', '{{ $json.emailSubject }}', '{{ $json.uploadedFile }}', '{{ $json.uploadDate }}')
```

### Slack Notifications

Add a Slack node after "Format Output":

```javascript
{
  "channel": "#attachments",
  "text": "📎 New attachment from *{{ $json.senderEmail }}*\nFile: {{ $json.fileName }} ({{ ($json.fileSize / 1024).toFixed(2) }} KB)\nSubject: {{ $json.emailSubject }}"
}
```

### Google Drive Alternative

Replace Dropbox nodes with Google Drive nodes:
- "Create Folder" → Google Drive Create Folder
- "Upload to Dropbox" → Google Drive Upload

## Performance Optimization

### For High Email Volume

1. **Increase Polling Interval** (IMAP):
   - Change from 5 min to 1 min for faster processing
   - Or use Gmail version for real-time webhooks

2. **Batch Processing**:
   - Add a "Split In Batches" node after email trigger
   - Process 10 emails at a time

3. **Queue Management**:
   - Use n8n's built-in queue mode
   - Set max concurrent executions

4. **Resource Allocation**:
   - Increase n8n memory limit
   - Use dedicated server for n8n

### For Large Attachments

1. **Streaming Upload**:
   - Enable streaming in Dropbox node settings

2. **Compression** (optional):
   - Add a "Compress" node before upload
   - Only for supported file types

3. **Cloud Storage**:
   - Ensure n8n has sufficient disk space
   - Use SSD for better performance

## Security Considerations

### Email Credentials

- ✅ Use OAuth2 when available (Gmail, Outlook)
- ✅ Use app-specific passwords instead of main password
- ✅ Enable 2FA on email account
- ❌ Don't store plain passwords in workflow

### Dropbox Access

- ✅ Use OAuth2 instead of access tokens
- ✅ Limit Dropbox app permissions to specific folder
- ✅ Regularly review connected apps in Dropbox
- ✅ Use team folders for business use

### n8n Instance

- ✅ Use HTTPS for n8n instance
- ✅ Enable authentication on n8n
- ✅ Keep n8n updated to latest version
- ✅ Use environment variables for sensitive data
- ✅ Backup workflow configurations regularly

### Data Privacy

- Consider data residency requirements
- Encrypt sensitive attachments before upload
- Implement data retention policies
- Add access logging for compliance

## Monitoring & Maintenance

### Execution Logs

Check n8n execution history:
- View successful executions
- Review failed executions
- Monitor execution time
- Track data throughput

### Error Alerts

Set up error notifications:
1. Add "Error Trigger" workflow
2. Configure to send alerts on failures
3. Include error details and execution ID

### Regular Maintenance

- **Weekly**: Review execution logs
- **Monthly**: Clean up old executions
- **Quarterly**: Review and optimize workflow
- **Yearly**: Audit credentials and permissions

## Use Cases

### Business Use Cases

1. **Invoice Management**
   - Auto-organize invoices by vendor
   - Store in accounting-ready structure
   - Integration with accounting software

2. **HR Document Management**
   - Organize resumes by applicant
   - Store employee documents
   - Compliance documentation

3. **Customer Support**
   - Organize support tickets by customer
   - Store screenshots and logs
   - Link to CRM system

4. **Legal Documents**
   - Organize contracts by client
   - Version control for amendments
   - Secure storage with audit trail

### Personal Use Cases

1. **Receipt Management**
   - Auto-organize receipts by sender
   - Store for tax purposes
   - Link to expense tracking

2. **Photo Backup**
   - Auto-backup photos from email
   - Organize by sender (family/friends)
   - Preserve memories

3. **Document Archive**
   - Store statements and bills
   - Organize by service provider
   - Easy retrieval when needed

## Support & Resources

### n8n Resources
- **Documentation**: https://docs.n8n.io
- **Community Forum**: https://community.n8n.io
- **GitHub**: https://github.com/n8n-io/n8n

### API Documentation
- **Dropbox API**: https://www.dropbox.com/developers/documentation
- **Gmail API**: https://developers.google.com/gmail/api
- **IMAP Protocol**: https://tools.ietf.org/html/rfc3501

### Getting Help

1. Check n8n community forum
2. Review execution logs for errors
3. Test with manual execution
4. Contact n8n support (cloud users)
5. Open GitHub issue for bugs

## License

These workflows are provided as-is under MIT License. Feel free to modify and distribute.

## Changelog

### Version 1.0.0 (2025-11-06)
- Initial release
- IMAP and Gmail versions
- Basic attachment processing
- Sender-based organization
- Error handling

## Contributing

Improvements and suggestions welcome!

Common enhancement ideas:
- OCR for scanned documents
- Virus scanning integration
- Metadata extraction
- Thumbnail generation
- Full-text search integration
- AI-powered categorization

---

**Created**: November 2025
**Last Updated**: November 2025
**Tested with**: n8n v1.x, Dropbox API v2, Gmail API v1
