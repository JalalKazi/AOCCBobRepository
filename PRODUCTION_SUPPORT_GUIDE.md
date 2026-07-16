# 🚨 Production Support & Incident Handling Guide
## Carhartt Reporting Bot - Critical Support Reference

---

## ⚡ QUICK REFERENCE CARD

### Bot Execution Schedule
- **Daily Run Time:** 6:00 AM IST
- **Expected Completion:** 6:30 AM IST (30 min max)
- **Critical Deadline:** 8:00 AM IST (Report must be delivered)

### Emergency Contacts
| Role | Contact | Escalation Time |
|------|---------|-----------------|
| **L1 Support** | [Phone/Email] | Immediate |
| **L2 Support** | [Phone/Email] | 15 minutes |
| **RPA Developer** | Anima Lal | 30 minutes |
| **Business Owner** | [Phone/Email] | 1 hour |

### Critical File Paths
```
Config:      C:\RPAProcesses\Report_Bot\Config\Bot_Config.xlsx
Logs:        C:\RPAProcesses\Report_Bot\Audit_logs\
Daily Report: C:\RPAProcesses\Report_Bot\Daily_Report\
SharePoint:  [Check General_Config sheet in Bot_Config.xlsx]
```

---

## 🔴 CRITICAL FAILURE SCENARIOS

### Scenario 1: Bot Fails to Start

**Symptoms:**
- No execution log created
- No email notification received
- Control Room shows "Failed to start"

**Immediate Actions (5 minutes):**
1. Check bot runner machine is online
2. Verify Outlook is running: `tasklist | findstr OUTLOOK`
3. Check disk space: `dir C:\ | findstr "bytes free"`
4. Verify service account not locked: Check Active Directory

**Resolution Steps:**
```powershell
# Step 1: Kill hung processes
taskkill /F /IM EXCEL.EXE
taskkill /F /IM OUTLOOK.EXE

# Step 2: Restart Outlook
Start-Process "outlook.exe"
Start-Sleep -Seconds 30

# Step 3: Rerun bot from Control Room
```

**Escalate If:** Machine offline, service account locked, or disk full

---

### Scenario 2: SharePoint Connection Failure

**Symptoms:**
- Log shows: "Issue in copying sharepoint file. Retry no: 10"
- Bot fails after 10 retry attempts
- Error email mentions SharePoint

**Immediate Actions (10 minutes):**
1. **Test SharePoint Access:**
   ```powershell
   # Open PowerShell as service account
   Test-Path "\\sharepoint\path\to\Master.xlsx"
   ```

2. **Check Network Connectivity:**
   ```powershell
   Test-Connection sharepoint.company.com
   ```

3. **Verify File Not Locked:**
   - Open SharePoint in browser
   - Check if file is checked out by another user
   - Check "Manage Access" for permissions

**Quick Fix:**
```powershell
# If file is locked, force close
Get-Process | Where-Object {$_.MainWindowTitle -like "*Master.xlsx*"} | Stop-Process -Force
```

**Manual Workaround:**
1. Copy SharePoint file manually to: `C:\RPAProcesses\Report_Bot\Main_Report\`
2. Rerun bot (it will use local copy)
3. After success, manually copy updated file back to SharePoint

**Escalate If:** Network down, permissions denied, or file corrupted

---

### Scenario 3: Outlook Not Connected

**Symptoms:**
- Log shows: "Outlook is connected" never appears
- Bot fails at email retrieval step
- Error: "Outlook not available"

**Immediate Actions (5 minutes):**
1. **Check Outlook Status:**
   ```powershell
   Get-Process outlook -ErrorAction SilentlyContinue
   ```

2. **Restart Outlook:**
   ```powershell
   Stop-Process -Name outlook -Force
   Start-Sleep -Seconds 10
   Start-Process "C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE"
   Start-Sleep -Seconds 30
   ```

3. **Verify Profile Loaded:**
   - Open Outlook manually
   - Check "Report" folder is visible
   - Verify emails from yesterday are present

**Common Issues:**
- **Outlook in Safe Mode:** Close and restart normally
- **Profile Not Loaded:** Wait 60 seconds for sync
- **Cached Mode Disabled:** Enable in Account Settings

**Escalate If:** Outlook crashes repeatedly or profile corrupted

---

### Scenario 4: Missing Input Files

**Symptoms:**
- Daily report shows zero counts for one or more bots
- Log shows: "Input excel file not exist with correct excel formatting"
- No errors but metrics are all zeros

**Immediate Actions (15 minutes):**
1. **Check Email Folder:**
   - Open Outlook → "Report" folder
   - Filter emails by yesterday's date
   - Verify report emails are present

2. **Check Input Folders:**
   ```powershell
   # Check each bot's input folder
   Get-ChildItem "C:\RPAProcesses\Report_Bot\*\Input" -Recurse
   ```

3. **Verify Email Keywords:**
   - Open Bot_Config.xlsx
   - Check "Keyword" column matches email subjects
   - Verify "FileKeyword" matches attachment names

**Manual Workaround:**
1. Download missing attachments manually from Outlook
2. Save to correct input folder: `C:\RPA\Input\[BotName]\`
3. Rerun bot

**Root Causes:**
- Source bot didn't run yesterday
- Email subject changed (keyword mismatch)
- Attachment not included in email
- Email sent to wrong folder

**Escalate If:** Source bot failure or systematic email delivery issue

---

### Scenario 5: Excel File Corruption

**Symptoms:**
- Log shows: "Error Message: [Excel error] at line [number]"
- Bot processes some files but fails on specific file
- Error mentions "file format" or "cannot open"

**Immediate Actions (10 minutes):**
1. **Identify Corrupted File:**
   - Check log for file path
   - Note which bot's file is causing issue

2. **Attempt File Repair:**
   ```powershell
   # Try opening in Excel with repair
   # File → Open → Browse → Select file → Open dropdown → Open and Repair
   ```

3. **Check File Extension:**
   ```powershell
   Get-ChildItem "C:\RPA\Input\*" -Recurse | Where-Object {$_.Extension -notin @('.xlsx','.xls','.csv')}
   ```

**Quick Fix:**
1. Move corrupted file to archive
2. Request source bot to resend report
3. Rerun reporting bot

**Prevention:**
- Ensure source bots save files properly
- Validate file format before sending
- Implement file integrity checks

**Escalate If:** Multiple files corrupted or systematic issue

---

### Scenario 6: Configuration File Missing/Corrupted

**Symptoms:**
- Bot fails immediately after start
- Error: "Config file missing" or "Invalid config structure"
- Log shows error at configuration loading step

**Immediate Actions (5 minutes):**
1. **Verify Config File Exists:**
   ```powershell
   Test-Path "C:\RPAProcesses\Report_Bot\Config\Bot_Config.xlsx"
   ```

2. **Check File Accessibility:**
   ```powershell
   # Try opening file
   Start-Process excel.exe -ArgumentList "C:\RPAProcesses\Report_Bot\Config\Bot_Config.xlsx"
   ```

3. **Restore from Backup:**
   - Check archive folder for recent backup
   - Copy backup to Config folder
   - Verify sheets: "Sheet1" and "General_Config"

**Critical Config Elements:**
- **Sheet1:** Bot configurations (8 columns)
- **General_Config:** SharePoint path, email addresses, main file path

**Escalate If:** No backup available or structure changed

---

## 🟡 WARNING SCENARIOS (Non-Critical)

### Warning 1: Partial Success (Some Bots Missing)

**Symptoms:**
- Daily report generated but some bots show zero counts
- Log shows warnings but no errors
- Email received with incomplete data

**Actions:**
1. Identify missing bots from daily report
2. Check if source bot ran yesterday
3. Verify input files in respective folders
4. Manually add data if available
5. Document in remarks column

**Impact:** Low - Report delivered but incomplete

---

### Warning 2: Slow Execution (>45 minutes)

**Symptoms:**
- Bot still running after 45 minutes
- No errors but taking longer than usual
- Control Room shows "In Progress"

**Actions:**
1. Check CPU/Memory usage on bot runner
2. Verify no other processes consuming resources
3. Check network latency to SharePoint
4. Review log for retry attempts
5. Allow bot to complete (max 2 hours)

**Impact:** Medium - May miss 8:00 AM deadline

---

### Warning 3: Retry Attempts (1-5 retries)

**Symptoms:**
- Log shows: "Issue in copying file. Retry no: 1-5"
- Bot eventually succeeds
- Execution time slightly longer

**Actions:**
1. Note retry count and reason
2. Monitor for pattern (same time daily)
3. Check SharePoint performance
4. Document for trend analysis

**Impact:** Low - Self-recovered

---

## 📋 INCIDENT RESPONSE CHECKLIST

### Phase 1: Detection (0-5 minutes)
- [ ] Failure email received
- [ ] Check Control Room status
- [ ] Review execution log
- [ ] Identify failure scenario (use scenarios above)
- [ ] Assess impact (critical/high/medium/low)

### Phase 2: Initial Response (5-15 minutes)
- [ ] Acknowledge incident (reply to failure email)
- [ ] Attempt quick fix based on scenario
- [ ] Document actions taken
- [ ] Determine if escalation needed
- [ ] Notify stakeholders if critical

### Phase 3: Resolution (15-60 minutes)
- [ ] Execute resolution steps
- [ ] Rerun bot if needed
- [ ] Verify successful completion
- [ ] Validate output (daily report and SharePoint)
- [ ] Send confirmation to stakeholders

### Phase 4: Post-Incident (1-24 hours)
- [ ] Complete incident ticket
- [ ] Document root cause
- [ ] Update knowledge base
- [ ] Identify preventive measures
- [ ] Schedule follow-up if needed

---

## 🔍 DIAGNOSTIC COMMANDS

### System Health Checks
```powershell
# Check bot runner machine
Get-ComputerInfo | Select-Object CsName, OsVersion, OsUptime

# Check disk space (must have >1GB free)
Get-PSDrive C | Select-Object Used, Free

# Check running processes
Get-Process | Where-Object {$_.Name -in @('outlook','excel','AABotAgent')}

# Check network connectivity
Test-Connection sharepoint.company.com -Count 4
Test-Connection mail.company.com -Count 4

# Check service account status
net user [ServiceAccountName] /domain
```

### File System Checks
```powershell
# List recent log files
Get-ChildItem "C:\RPAProcesses\Report_Bot\Audit_logs\" -Filter "*.txt" | 
    Sort-Object LastWriteTime -Descending | Select-Object -First 5

# Check input folders for files
Get-ChildItem "C:\RPA\Input\*" -Recurse -File | 
    Group-Object Directory | Select-Object Name, Count

# Verify daily report created
Get-ChildItem "C:\RPAProcesses\Report_Bot\Daily_Report\" -Filter "*.xlsx" |
    Where-Object {$_.LastWriteTime -gt (Get-Date).AddDays(-1)}

# Check SharePoint file accessibility
Test-Path "\\sharepoint\path\to\Master.xlsx"
```

### Application Checks
```powershell
# Check Outlook connection
$outlook = New-Object -ComObject Outlook.Application
$namespace = $outlook.GetNamespace("MAPI")
$folder = $namespace.GetDefaultFolder(6) # Inbox
Write-Host "Outlook Status: Connected"

# Check Excel version
$excel = New-Object -ComObject Excel.Application
Write-Host "Excel Version: $($excel.Version)"
$excel.Quit()

# Check AA360 Control Room connectivity
# (Use Control Room web interface)
```

---

## 📊 LOG FILE ANALYSIS

### Understanding Log Entries

**Normal Execution Pattern:**
```
[07:15:23] Report Bot Execution Started.
[07:15:25] Config file is opened
[07:15:30] Outlook is connected
[07:15:45] Input file is downloaded and pasted to C:\RPA\Input\PO_Creation
[07:16:00] Subtask execution initiated for Indirect PO Creation
[07:16:15] C:\RPA\Input\PO_Creation\PO_Summary.xlsx started processing.
[07:20:30] Copy sharepoint file to main file.
[07:21:00] Sharepoint has been updated
[07:21:15] Report has sent to support team.
[07:21:20] Report Bot Execution completed.
```

**Error Indicators:**
- `Issue in copying` → SharePoint connectivity problem
- `Error Message:` → Exception occurred
- `at line number` → Code execution failure
- `Retry no:` → Transient failure with retry

**Warning Indicators:**
- `Input excel file not exist` → Missing input file
- `File copied to Archive` → Cleanup activity
- `Deleted from Input files` → Normal housekeeping

### Log Analysis Commands
```powershell
# Get today's log file
$logFile = Get-ChildItem "C:\RPAProcesses\Report_Bot\Audit_logs\" | 
    Sort-Object LastWriteTime -Descending | Select-Object -First 1

# Search for errors
Select-String -Path $logFile.FullName -Pattern "Error|Failed|Issue"

# Search for specific bot
Select-String -Path $logFile.FullName -Pattern "Indirect PO Creation"

# Count retry attempts
(Select-String -Path $logFile.FullName -Pattern "Retry no:").Count

# Extract execution timeline
Get-Content $logFile.FullName | Select-String -Pattern "\[\d{2}:\d{2}:\d{2}\]"
```

---

## 🛠️ MANUAL RECOVERY PROCEDURES

### Procedure 1: Manual Report Generation

**When to Use:** Bot completely failed, deadline approaching

**Steps:**
1. **Collect Input Files:**
   ```powershell
   # Download from Outlook manually
   # Save to: C:\RPA\Input\[BotName]\
   ```

2. **Open Daily Template:**
   - Copy previous day's report
   - Update date to yesterday
   - Clear data rows (keep headers)

3. **Process Each Bot Manually:**
   - Open bot's Excel file
   - Count rows by status:
     - Volume = Total rows (excluding header)
     - Success = Rows with "Success" status
     - Exception = Rows with "Exception" or "Parked"
     - Failure = Remaining rows
   - Enter counts in daily report

4. **Update SharePoint:**
   - Open master file from SharePoint
   - Copy daily data
   - Paste at end of master file
   - Save and close

5. **Send Email:**
   - Compose email to stakeholders
   - Attach daily report
   - Mention "Manual Report - Bot Failed"

**Time Required:** 60-90 minutes

---

### Procedure 2: Rerun Bot After Fix

**When to Use:** Issue resolved, need to regenerate report

**Steps:**
1. **Clean Up Previous Run:**
   ```powershell
   # Delete partial daily report
   Remove-Item "C:\RPAProcesses\Report_Bot\Daily_Report\*.xlsx" -Force
   
   # Clear input folders (if needed)
   Get-ChildItem "C:\RPA\Input\*" -Recurse -File | Remove-Item -Force
   ```

2. **Verify Prerequisites:**
   - [ ] Outlook running and connected
   - [ ] SharePoint accessible
   - [ ] Config file present
   - [ ] Input files available (or will be downloaded)

3. **Trigger Bot:**
   - Open Control Room
   - Navigate to bot: "Report_Main"
   - Click "Run" → "Run Now"
   - Monitor execution in real-time

4. **Verify Success:**
   - Check for completion email
   - Open daily report and verify data
   - Check SharePoint file updated
   - Review execution log

---

### Procedure 3: Emergency Configuration Update

**When to Use:** Need to add/remove bot or change settings urgently

**Steps:**
1. **Backup Current Config:**
   ```powershell
   Copy-Item "C:\RPAProcesses\Report_Bot\Config\Bot_Config.xlsx" `
            "C:\RPAProcesses\Report_Bot\Config\Bot_Config_Backup_$(Get-Date -Format 'yyyyMMdd_HHmm').xlsx"
   ```

2. **Open Config File:**
   - Close any Excel processes first
   - Open Bot_Config.xlsx

3. **Make Changes:**
   - **Add Bot:** Insert new row in Sheet1 with all 8 columns
   - **Remove Bot:** Delete row (don't leave blank rows)
   - **Update Settings:** Modify values in existing rows
   - **Update Emails:** Change in General_Config sheet

4. **Validate Changes:**
   - [ ] No blank rows
   - [ ] All mandatory columns filled
   - [ ] Folder paths exist
   - [ ] Keywords match email subjects
   - [ ] Logic types are valid

5. **Test:**
   - Save and close file
   - Run bot in test mode (if available)
   - Or run in production and monitor closely

---

## 📈 MONITORING & ALERTS

### Daily Health Checks (8:00 AM)

**Automated Checks:**
- [ ] Completion email received
- [ ] Daily report attached
- [ ] No errors in log file
- [ ] All configured bots present in report
- [ ] SharePoint file updated

**Manual Checks:**
- [ ] Open daily report and spot-check data
- [ ] Compare with previous day for anomalies
- [ ] Verify total volume is reasonable
- [ ] Check remarks column for issues
- [ ] Review execution time (should be <30 min)

### Weekly Reviews (Monday 9:00 AM)

- [ ] Review past week's execution logs
- [ ] Analyze retry patterns
- [ ] Check for recurring warnings
- [ ] Validate data accuracy (sample check)
- [ ] Update knowledge base with new issues
- [ ] Review and close incident tickets

### Monthly Reviews (First Monday)

- [ ] Analyze success rate (target: 98%)
- [ ] Review average execution time
- [ ] Identify optimization opportunities
- [ ] Update configuration for new bots
- [ ] Archive old log files (>90 days)
- [ ] Test disaster recovery procedures

---

## 🚦 ESCALATION MATRIX

### Level 1: L1 Support (0-15 minutes)
**Handles:**
- Routine failures with known fixes
- File missing issues
- Simple restarts
- Log file analysis

**Escalate When:**
- Unknown error messages
- Multiple retry failures
- Configuration issues
- Service account problems

### Level 2: L2 Support (15-30 minutes)
**Handles:**
- Complex troubleshooting
- Configuration changes
- Manual recovery procedures
- Root cause analysis

**Escalate When:**
- Code changes required
- Infrastructure issues
- Permissions problems
- Systematic failures

### Level 3: RPA Developer (30-60 minutes)
**Handles:**
- Bot code modifications
- Logic type changes
- New bot integration
- Performance optimization

**Escalate When:**
- Platform issues
- Architecture changes
- Major enhancements needed

### Level 4: Business Owner (1+ hours)
**Handles:**
- Business decisions
- SLA exceptions
- Process changes
- Stakeholder communication

---

## 📞 COMMUNICATION TEMPLATES

### Template 1: Incident Notification

**Subject:** URGENT: Daily Report Bot Failed - [Date]

**Body:**
```
Team,

The Daily Report Bot failed during execution at [Time].

Error: [Brief description]
Impact: Daily report not delivered
ETA for Resolution: [Time]

Actions Taken:
1. [Action 1]
2. [Action 2]

Current Status: [Investigating/In Progress/Resolved]

Will update in 15 minutes.

[Your Name]
L1/L2 Support
```

---

### Template 2: Resolution Notification

**Subject:** RESOLVED: Daily Report Bot - [Date]

**Body:**
```
Team,

The Daily Report Bot issue has been resolved.

Root Cause: [Brief explanation]
Resolution: [What was done]
Report Status: Delivered at [Time]

Preventive Actions:
- [Action 1]
- [Action 2]

Incident Ticket: [Ticket Number]

[Your Name]
L1/L2 Support
```

---

### Template 3: Manual Report Notification

**Subject:** Daily Status Report - [Date] (Manual)

**Body:**
```
Hi All,

Please find the Daily status report attached.

Note: This report was generated manually due to bot failure.
All data has been verified for accuracy.

Bot Status: Under investigation
Next Steps: [Brief description]

Regards,
RPA Support Team
```

---

## 🎯 KEY PERFORMANCE INDICATORS (KPIs)

### Track These Metrics:

| KPI | Target | Measurement | Action If Below Target |
|-----|--------|-------------|------------------------|
| **Success Rate** | 98% | Successful runs / Total runs | Investigate recurring failures |
| **Avg Execution Time** | <30 min | Sum of times / Number of runs | Optimize slow steps |
| **MTTR** | <1 hour | Time to resolve incidents | Improve troubleshooting |
| **Manual Interventions** | <2/month | Count of manual reports | Enhance error handling |
| **SLA Compliance** | 100% | Reports by 8 AM / Total days | Adjust schedule or resources |

---

## 📚 KNOWLEDGE BASE ARTICLES

### KB-001: SharePoint File Locked
**Problem:** Cannot copy file from SharePoint  
**Solution:** Check file checkout status, force close Excel processes  
**Prevention:** Implement file locking checks

### KB-002: Outlook Profile Not Loaded
**Problem:** Bot cannot connect to Outlook  
**Solution:** Wait 60 seconds, restart Outlook  
**Prevention:** Add profile load verification

### KB-003: Missing Input Files
**Problem:** Zero counts for specific bot  
**Solution:** Check source bot execution, verify email keywords  
**Prevention:** Implement pre-execution validation

### KB-004: Disk Space Full
**Problem:** Cannot create files  
**Solution:** Clean up old logs and archives  
**Prevention:** Implement automated cleanup

### KB-005: Configuration Mismatch
**Problem:** Bot processes wrong files  
**Solution:** Verify keywords and file paths in config  
**Prevention:** Implement config validation

---

## ✅ PRODUCTION READINESS CHECKLIST

### Before Go-Live:
- [ ] All prerequisites installed and configured
- [ ] Service account created with required permissions
- [ ] Configuration file populated and validated
- [ ] Folder structure created
- [ ] SharePoint access tested
- [ ] Outlook connection tested
- [ ] Test execution successful
- [ ] Stakeholders trained
- [ ] Support team trained
- [ ] Runbook reviewed and approved
- [ ] Escalation contacts confirmed
- [ ] Monitoring alerts configured
- [ ] Backup and recovery tested

### Post Go-Live (First Week):
- [ ] Monitor daily executions closely
- [ ] Validate output accuracy
- [ ] Gather stakeholder feedback
- [ ] Fine-tune configuration
- [ ] Update documentation
- [ ] Conduct lessons learned session

---

## 🔐 SECURITY REMINDERS

### DO:
✅ Use service account for bot execution  
✅ Store credentials in Windows Credential Manager  
✅ Restrict access to configuration files  
✅ Review audit logs regularly  
✅ Follow change management process  
✅ Document all manual interventions

### DON'T:
❌ Share service account password  
❌ Hardcode credentials in bot  
❌ Modify production config without approval  
❌ Delete log files prematurely  
❌ Bypass security controls  
❌ Run bot with personal account

---

## 📝 INCIDENT LOG TEMPLATE

```
Incident ID: INC-[YYYYMMDD-###]
Date/Time: [Date] [Time]
Reported By: [Name]
Severity: [Critical/High/Medium/Low]

Description:
[What happened]

Impact:
[Business impact]

Root Cause:
[Why it happened]

Resolution:
[What was done]

Time to Resolve: [Minutes]

Preventive Actions:
1. [Action 1]
2. [Action 2]

Lessons Learned:
[Key takeaways]

Closed By: [Name]
Closed Date: [Date]
```

---

## 🆘 EMERGENCY HOTLINE

**For Critical Production Issues:**

📞 **L1 Support:** [Phone Number]  
📞 **L2 Support:** [Phone Number]  
📞 **RPA Developer:** [Phone Number]  
📧 **Email:** rpa.support@company.com  
💬 **Teams Channel:** RPA Support  
🎫 **Ticket System:** [URL]

**Available:** 8:00 AM - 6:00 PM IST (Monday-Friday)  
**After Hours:** Email only (4-hour response SLA)

---

**Document Version:** 1.0  
**Last Updated:** June 16, 2026  
**Next Review:** September 16, 2026  
**Owner:** RPA Support Team

---

**🔴 REMEMBER: When in doubt, escalate early! 🔴**