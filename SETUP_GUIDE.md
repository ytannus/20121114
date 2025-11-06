# n8n Email Attachments to Dropbox - Setup Guide

## Quick Setup (5 Minutes)

### Step 1: Import the Workflow

1. Open your n8n instance
2. Click **"+"** → **"Import from File"**
3. Upload `n8n-email-to-dropbox-fixed.json`
4. Click **"Import"**

### Step 2: Configure Email (IMAP) Credentials

1. Click on the **"Email Trigger"** node
2. Click **"Credential to connect with"**
3. Click **"+ Create New Credential"**
4. Select **"IMAP"**
5. Fill in your email settings:

#### Gmail:
```
User: your.email@gmail.com
Password: your-app-specific-password
Host: imap.gmail.com
Port: 993
Security: SSL/TLS
```

**Note**: For Gmail, you need to create an App Password:
- Go to: https://myaccount.google.com/apppasswords
- Create new app password for "Mail"
- Use that password (not your regular password)

#### Outlook/Office 365:
```
User: your.email@outlook.com
Password: your-password
Host: outlook.office365.com
Port: 993
Security: SSL/TLS
```

#### Yahoo Mail:
```
User: your.email@yahoo.com
Password: your-app-password
Host: imap.mail.yahoo.com
Port: 993
Security: SSL/TLS
```

6. Click **"Create"**

### Step 3: Configure Dropbox Credentials

**Option A: Access Token (Easiest)**

1. Go to: https://www.dropbox.com/developers/apps
2. Click **"Create app"**
3. Choose:
   - Scoped access
   - Full Dropbox
   - Name: "n8n Email Attachments"
4. Click **"Create app"**
5. Under **"Permissions"** tab, enable:
   - `files.content.write`
   - `files.content.read`
6. Under **"Settings"** tab, click **"Generate access token"**
7. Copy the token

In n8n:
1. Click on **"Create Sender Folder"** node
2. Click **"Credential to connect with"**
3. Click **"+ Create New Credential"**
4. Select **"Dropbox API"**
5. Choose **"Access Token"**
6. Paste your token
7. Click **"Create"**

**Option B: OAuth2 (More Secure)**

1. Follow steps 1-5 from Option A
2. Under **"Settings"** tab:
   - Add Redirect URI: `https://your-n8n-url/rest/oauth2-credential/callback`
   - Copy App key and App secret
3. In n8n:
   - Select **"OAuth2"**
   - Enter App key and App secret
   - Click **"Connect my account"**
   - Authorize access
   - Click **"Create"**

### Step 4: Link Dropbox Credential to Upload Node

1. Click on **"Upload to Dropbox"** node
2. Click **"Credential to connect with"**
3. Select the same Dropbox credential you just created
4. Click outside the node to save

### Step 5: Activate and Test

1. Click **"Save"** (top right)
2. Toggle **"Active"** (top right) to ON
3. Send a test email to your inbox with an attachment
4. Wait 5 minutes (default poll interval)
5. Check n8n executions (left sidebar → Executions)
6. Check Dropbox → Emails folder should be created

## Folder Structure

After processing emails, Dropbox will have:

```
/Emails/
  ├── sender1@example.com/
  │   ├── file1.pdf
  │   └── file2.jpg
  ├── sender2@company.com/
  │   └── document.docx
  └── support@service.com/
      └── ticket.pdf
```

## Customization

### Change Base Folder

To use a different base folder (e.g., `/Attachments/` instead of `/Emails/`):

1. Click **"Create Sender Folder"** node
2. Change path from:
   ```
   /Emails/{{ $json.dropboxFolder }}
   ```
   To:
   ```
   /Attachments/{{ $json.dropboxFolder }}
   ```

3. Click **"Upload to Dropbox"** node
4. Change path from:
   ```
   /Emails/{{ $json.senderFolder }}/{{ $json.filename }}
   ```
   To:
   ```
   /Attachments/{{ $json.senderFolder }}/{{ $json.filename }}
   ```

### Adjust Email Check Frequency

1. Click **"Email Trigger"** node
2. Scroll to **"Options"** section
3. Add **"Custom Email Config"**
4. Adjust polling interval (default is 5 minutes)

### Filter by File Type

To only process PDF files:

1. Add an **"IF"** node after **"Prepare Upload Data"**
2. Condition:
   ```
   {{ $json.contentType.includes('pdf') }}
   ```
3. Connect TRUE branch to **"Upload to Dropbox"**

### Add Date Subfolders

To organize by month (e.g., `/Emails/sender@email.com/2025-11/`):

1. Click **"Upload to Dropbox"** node
2. Change path to:
   ```
   /Emails/{{ $json.senderFolder }}/{{ $now.format('yyyy-MM') }}/{{ $json.filename }}
   ```

## Troubleshooting

### Issue: "IMAP connection failed"

**Solutions:**
- Check username and password are correct
- For Gmail: Use App Password, not regular password
- Verify IMAP is enabled in your email settings
- Check firewall allows connection to IMAP port
- Try disabling "Allow Unauthorized Certs" in Email Trigger options

### Issue: "Dropbox credential error"

**Solutions:**
- Verify access token is valid (they don't expire for Dropbox)
- Check app has correct permissions (`files.content.write`)
- Try regenerating the access token
- Ensure no spaces before/after token when pasting

### Issue: "Folder already exists" error

**Solution:** This is normal! The workflow has `continueOnFail: true` on folder creation, so it will proceed even if folder exists.

### Issue: Attachments not uploading

**Check:**
1. Dropbox has sufficient storage space
2. File names don't contain invalid characters
3. Binary data is present in **"Split Attachments"** output
4. Test manually:
   - Click **"Email Trigger"** → **"Execute Node"**
   - Check if attachments are listed in output

**Debug:**
- Check each node output step by step
- Look for error messages in execution logs
- Verify binary data property is `data` (default)

### Issue: Workflow not triggering

**Solutions:**
- Check workflow is **Active** (toggle in top right)
- Verify email credential is valid
- Check IMAP connection settings
- Look at execution history for errors
- Try **"Test Workflow"** button with manual execution

### Issue: Special characters in filenames

**Solution:** Add filename sanitization in **"Prepare Upload Data"** node:

Change filename assignment to:
```
{{ $json.filename.replace(/[^a-zA-Z0-9._-]/g, '_') }}
```

### Issue: Large files failing

**Solutions:**
- Files over 150MB need special handling
- Check n8n timeout settings
- Increase execution timeout in n8n settings
- For very large files, consider using Dropbox's chunked upload API

## Testing the Workflow

### Manual Test

1. Click **"Email Trigger"** node
2. Click **"Execute Node"**
3. Should see recent emails in output
4. If email has attachments, continue through workflow
5. Check each node's output
6. Verify file uploaded to Dropbox

### Live Test

1. Activate workflow
2. Send test email to your inbox with an attachment
3. Wait 5 minutes (or your polling interval)
4. Check **"Executions"** in n8n sidebar
5. Should see successful execution
6. Check Dropbox for uploaded file

## Performance Tips

### For High Volume

- Reduce polling interval to 1-2 minutes
- Use Gmail with webhooks instead of IMAP polling
- Add queue management if processing many emails
- Consider splitting into multiple workflows by sender

### For Large Attachments

- Increase n8n memory allocation
- Use SSD storage for n8n
- Enable streaming uploads in Dropbox settings
- Consider file size limits

## Security Best Practices

✅ **Email:**
- Use app-specific passwords (not main password)
- Enable 2FA on email account
- Don't share IMAP credentials

✅ **Dropbox:**
- Use OAuth2 when possible
- Limit app permissions to specific folder
- Regularly review connected apps
- Don't share access tokens

✅ **n8n:**
- Use HTTPS for n8n instance
- Enable n8n authentication
- Keep n8n updated
- Backup workflow configurations

## Common IMAP Settings

| Provider | Host | Port | Security |
|----------|------|------|----------|
| Gmail | imap.gmail.com | 993 | SSL/TLS |
| Outlook | outlook.office365.com | 993 | SSL/TLS |
| Yahoo | imap.mail.yahoo.com | 993 | SSL/TLS |
| iCloud | imap.mail.me.com | 993 | SSL/TLS |
| Zoho | imap.zoho.com | 993 | SSL/TLS |
| ProtonMail | 127.0.0.1 | 1143 | STARTTLS* |

*ProtonMail requires Bridge app

## Next Steps

After setup works:

1. **Organize Better**: Add date-based subfolders
2. **Filter Content**: Only process specific file types
3. **Add Notifications**: Send Slack/email when files uploaded
4. **Log to Database**: Track all uploads in database
5. **Integrate Systems**: Connect to your CRM/ERP

## Support

- Check n8n execution logs for detailed errors
- Review node outputs step by step
- Test with simple email first
- Verify all credentials before activating

**Workflow is ready to use once credentials are configured!** 🚀
