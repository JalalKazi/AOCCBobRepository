# Carhartt Reporting Bot - Support Runbook

**Platform:** Automation Anywhere A360  
**Bot Name:** Report_Main  
**Execution Frequency:** Daily (Scheduled)  
**Average Duration:** 15-30 minutes  
**Support Level:** L1/L2

---

## Table of Contents
1. [Daily Health Check](#1-daily-health-check)
2. [Pre-Execution Verification](#2-pre-execution-verification)
3. [Monitoring Active Execution](#3-monitoring-active-execution)
4. [Post-Execution Validation](#4-post-execution-validation)
5. [Troubleshooting Failed Runs](#5-troubleshooting-failed-runs)
6. [Common Issues & Resolutions](#6-common-issues--resolutions)
7. [Emergency Procedures](#7-emergency-procedures)
8. [Escalation Procedures](#8-escalation-procedures)

---

## 1. Daily Health Check

**Frequency:** Once per day (before scheduled run)  
**Time Required:** 5 minutes  
**Responsibility:** L1 Support

### Step-by-Step Actions

#### 1.1 Verify Bot Runner Machine Status
```
□ Step 1: Open Remote Desktop Connection
   - Server: [Bot Runner Machine Name]
   - Login with: [Service Account Credentials]

□ Step 2: Check Machine Health
   - CPU Usage < 80%: _____ (Current: ____%)
   - Memory Usage < 80%: _____ (Current: ____%)
   - C: Drive Free Space > 1GB: _____ (Current: ____GB)

□ Step 3: Verify No Hung Processes
   - Open Task Manager (Ctrl+Shift+Esc)
   - Check for hung Excel processes: _____ (Count: ____)
   - If found: Kill process (taskkill /t /IM EXCEL.EXE /f)
```

#### 1.2 Verify Outlook Status
```
□ Step 1: Check Outlook Application
   - Outlook is running: _____
   - Outlook is responsive (not "Not Responding"): _____
   - Can open Outlook manually: _____

□ Step 2: Verify "Report" Folder
   - Navigate to Outlook
   - Locate "Report" folder in folder list: _____
   - Folder is accessible: _____

□ Step 3: Check for Yesterday's Emails
   - Open "Report" folder
   - Filter by date: Yesterday
   - Count emails received: _____ (Expected: 5-10)
   - Emails have attachments: _____
```

#### 1.3 Verify SharePoint Connectivity
```
□ Step 1: Test SharePoint Path
   - Open File Explorer
   - Navigate to: [SharePoint UNC Path from config]
   - Path is accessible: _____
   - Can open Master_Report.xlsx: _____

□ Step 2: Check File Lock Status
   - Right-click Master_Report.xlsx → Properties
   - File is not locked by another user: _____
   - If locked, note user: _____________
```

#### 1.4 Verify Configuration Files
```
□ Step 1: Check Config File Exists
   - Navigate to: C:\RPAProcesses\Report_Bot\Config
   - Bot_Config.xlsx exists: _____
   - File size > 0 KB: _____

□ Step 2: Open and Validate Config
   - Open Bot_Config.xlsx
   - Sheet1 exists with data: _____
   - General_Config sheet exists: _____
   - No #REF! or #VALUE! errors: _____
   - Close file
```

#### 1.5 Check Previous Run Status
```
□ Step 1: Review Control Room
   - Login to AA360 Control Room
   - Navigate to: Activity → Bot Activity
   - Filter: Bot Name = "Report_Main"
   - Last run status: _____ (Success/Failed)
   - Last run date: _____________
   - Last run duration: _____ minutes

□ Step 2: Review Log File
   - Navigate to: C:\RPAProcesses\Report_Bot\Audit_logs
   - Open latest Log_file*.txt
   - Last entry shows "completed": _____
   - No error messages in last 20 lines: _____
```

**Health Check Result:**
- [ ] All checks passed - Bot ready for execution
- [ ] Issues found - Document below and resolve before run

**Issues Found:**
```
Issue 1: _________________________________________________
Action Taken: ____________________________________________

Issue 2: _________________________________________________
Action Taken: ____________________________________________
```

---

## 2. Pre-Execution Verification

**When to Perform:** 15 minutes before scheduled run  
**Time Required:** 3 minutes  
**Responsibility:** L1 Support

### Step-by-Step Actions

#### 2.1 Verify Input Files Available
```
□ Step 1: Check Email Attachments Downloaded
   - Open Outlook "Report" folder
   - Verify emails from yesterday with subject keywords:
     • "PO Creation Report": _____
     • "PR Creation Report": _____
     • "Delivery Recon Report": _____
     • "RTL Mass PO Report": _____
     • [Add other bot keywords]: _____

□ Step 2: Verify Attachment Format
   - Each email has Excel attachment (.xlsx/.xls/.csv): _____
   - Attachments can be opened manually: _____
```

#### 2.2 Clear Previous Run Artifacts
```
□ Step 1: Clean Input Folders (if needed)
   - Navigate to: C:\RPAProcesses\Report_Bot\Input\
   - Check each bot subfolder for old files
   - If files exist from previous failed run:
     • Move to respective Archive folder
     • Document: _________________________________

□ Step 2: Verify Daily Report Folder
   - Navigate to: C:\RPAProcesses\Report_Bot\Daily_Report
   - Check if today's file already exists
   - If exists: Rename with "_OLD" suffix
```

#### 2.3 Final System Check
```
□ Step 1: Verify No Active Bot Runs
   - Check Control Room → Activity → Running Bots
   - Report_Main is not currently running: _____

□ Step 2: Verify Disk Space
   - C: Drive free space > 1GB: _____

□ Step 3: Verify Network Connectivity
   - Ping SharePoint server: _____
   - Ping mail server: _____
```

**Pre-Execution Status:**
- [ ] Ready for execution
- [ ] Not ready - Issues documented below

**Issues:**
```
_____________________________________________________________
_____________________________________________________________
```

---

## 3. Monitoring Active Execution

**When to Perform:** During bot execution  
**Time Required:** Periodic checks every 5 minutes  
**Responsibility:** L1 Support

### Step-by-Step Actions

#### 3.1 Monitor Bot Progress (Every 5 Minutes)
```
□ Step 1: Check Control Room Status
   - Login to Control Room
   - Navigate to: Activity → Running Bots
   - Locate: Report_Main
   - Status: _____ (Running/Completed/Failed)
   - Current step: _____________________________
   - Elapsed time: _____ minutes

□ Step 2: Check Expected Duration
   - Normal duration: 15-30 minutes
   - Current duration within range: _____
   - If > 45 minutes: Flag for investigation
```

#### 3.2 Monitor Log File (Real-Time)
```
□ Step 1: Open Latest Log File
   - Navigate to: C:\RPAProcesses\Report_Bot\Audit_logs
   - Open latest Log_file*.txt
   - Keep file open in Notepad++

□ Step 2: Watch for Key Milestones
   Time    Milestone                                    Status
   ____    "Report Bot Execution Started"              _____
   ____    "Config file is opened"                     _____
   ____    "Outlook is connected"                      _____
   ____    "Input file is downloaded"                  _____
   ____    "Subtask execution initiated" (per bot)    _____
   ____    "Copy sharepoint file to main file"        _____
   ____    "Sharepoint has been updated"               _____
   ____    "Report has sent to support team"          _____
   ____    "Report Bot Execution completed"            _____

□ Step 3: Watch for Errors
   - Any line containing "error", "failed", "exception": _____
   - If found, document: _________________________________
```

#### 3.3 Monitor System Resources
```
□ Step 1: Check Task Manager
   - Excel.exe CPU usage: ____% (Normal: <50%)
   - Excel.exe Memory: ____MB (Normal: <500MB)
   - Multiple Excel processes: _____ (Count: ____)

□ Step 2: Check for Hung Processes
   - Any "Not Responding" processes: _____
   - If yes, document: ___________________________________
```

#### 3.4 Monitor Email Activity
```
□ Step 1: Check Outlook Sent Items
   - Open Outlook → Sent Items
   - Look for "Daily Status Report" email
   - Email sent: _____ (Time: _____)
   - Has attachment: _____
```

**Monitoring Notes:**
```
Time: _____ - Observation: _________________________________
Time: _____ - Observation: _________________________________
Time: _____ - Observation: _________________________________
```

---

## 4. Post-Execution Validation

**When to Perform:** Immediately after bot completion  
**Time Required:** 5 minutes  
**Responsibility:** L1 Support

### Step-by-Step Actions

#### 4.1 Verify Bot Completion Status
```
□ Step 1: Check Control Room
   - Navigate to: Activity → Bot Activity
   - Filter: Report_Main, Today's date
   - Execution status: _____ (Success/Failed)
   - End time: _____
   - Total duration: _____ minutes
   - Error message (if failed): ___________________________

□ Step 2: Review Final Log Entry
   - Open latest log file
   - Last entry: "Report Bot Execution completed": _____
   - No errors in last 10 lines: _____
```

#### 4.2 Validate Output Files
```
□ Step 1: Check Daily Report File
   - Navigate to: C:\RPAProcesses\Report_Bot\Daily_Report
   - File exists: [Yesterday's date].xlsx: _____
   - File size > 10KB: _____
   - Open file and verify:
     • Headers present (Date, Bot Name, Volume, etc.): _____
     • Data rows present: _____ (Count: ____)
     • No #REF! or #VALUE! errors: _____
     • All configured bots listed: _____

□ Step 2: Check Master File Updated
   - Navigate to SharePoint path
   - Open Master_Report.xlsx
   - Check last row date = Yesterday: _____
   - Row count increased: _____ (Previous: ____, Current: ____)
   - Data looks correct: _____

□ Step 3: Check Archive Created
   - Navigate to: C:\RPAProcesses\Report_Bot\Archive\Main_Report
   - Archive file exists with today's timestamp: _____
```

#### 4.3 Verify Email Notifications
```
□ Step 1: Check Stakeholder Email
   - Open Outlook → Sent Items
   - Email sent to: [Configured recipients]
   - Subject: "Daily Status Report": _____
   - Attachment: [Yesterday's date].xlsx: _____
   - Email body contains standard message: _____

□ Step 2: Check Completion Email
   - Subject: "Daily Report Bot Completed": _____
   - Attachment: Log file: _____
   - Email sent: _____
```

#### 4.4 Validate Data Accuracy (Spot Check)
```
□ Step 1: Pick One Bot to Verify
   - Selected bot: _____________________________
   - Open input file for this bot
   - Manually count:
     • Total rows: _____
     • Success rows: _____
     • Exception rows: _____
     • Failure rows: _____

□ Step 2: Compare with Daily Report
   - Open daily report file
   - Find row for selected bot
   - Reported Volume: _____ (Match: _____)
   - Reported Success: _____ (Match: _____)
   - Reported Exception: _____ (Match: _____)
   - Reported Failure: _____ (Match: _____)

□ Step 3: Verify Totals
   - All counts match: _____
   - If mismatch, document: ______________________________
```

**Post-Execution Result:**
- [ ] All validations passed - Bot run successful
- [ ] Issues found - Document and escalate if needed

**Issues Found:**
```
Issue: ___________________________________________________
Severity: _____ (Low/Medium/High/Critical)
Action Required: _________________________________________
```

---

## 5. Troubleshooting Failed Runs

**When to Perform:** When bot execution fails  
**Time Required:** 15-30 minutes  
**Responsibility:** L1 Support

### Step-by-Step Troubleshooting

#### 5.1 Identify Failure Point
```
□ Step 1: Review Control Room Error
   - Navigate to: Activity → Bot Activity
   - Open failed run details
   - Error message: ______________________________________
   - Error line number: _____
   - Failed step: ________________________________________

□ Step 2: Review Log File
   - Open latest log file
   - Find last successful entry: _________________________
   - Find first error entry: _____________________________
   - Error details: ______________________________________

□ Step 3: Categorize Failure
   Select one:
   [ ] Outlook connection failure
   [ ] Email/attachment not found
   [ ] SharePoint access failure
   [ ] Excel file processing error
   [ ] Configuration file error
   [ ] System resource issue
   [ ] Other: ___________________________________________
```

#### 5.2 Outlook Connection Failure
```
IF Error contains "Outlook" or "Email":

□ Step 1: Verify Outlook Running
   - Open Task Manager
   - Outlook.exe is running: _____
   - If not: Start Outlook manually
   - Wait 30 seconds for profile to load

□ Step 2: Test Outlook Manually
   - Open Outlook application
   - Can see inbox: _____
   - Can navigate to "Report" folder: _____
   - Can see emails: _____

□ Step 3: Check Outlook Profile
   - Control Panel → Mail → Show Profiles
   - Default profile exists: _____
   - Profile name: _____________________________

□ Step 4: Restart Outlook
   - Close Outlook completely
   - Kill any hung processes: taskkill /IM outlook.exe /f
   - Restart Outlook
   - Wait 60 seconds for full load

□ Step 5: Retry Bot
   - Trigger bot manually from Control Room
   - Monitor execution
   - Result: _____ (Success/Failed)

IF STILL FAILING: Escalate to L2
```

#### 5.3 SharePoint Access Failure
```
IF Error contains "SharePoint" or "copying file":

□ Step 1: Test SharePoint Path
   - Open File Explorer
   - Navigate to SharePoint path from config
   - Path accessible: _____
   - If not accessible, error: ___________________________

□ Step 2: Check File Lock
   - Navigate to Master_Report.xlsx
   - Right-click → Properties
   - File locked by: _____ (User: _______)
   - If locked: Contact user to close file

□ Step 3: Check Permissions
   - Right-click Master_Report.xlsx → Properties → Security
   - Bot runner account listed: _____
   - Has Read/Write permissions: _____

□ Step 4: Test Network Connectivity
   - Open Command Prompt
   - ping [SharePoint server name]
   - Result: _____ (Success/Failed)
   - Packet loss: _____%

□ Step 5: Check Disk Space
   - SharePoint drive free space: ____GB
   - Sufficient space (>1GB): _____

□ Step 6: Retry Bot
   - Ensure file is not locked
   - Trigger bot manually
   - Monitor execution
   - Result: _____ (Success/Failed)

IF STILL FAILING: Escalate to L2
```

#### 5.4 Excel File Processing Error
```
IF Error contains "Excel" or "spreadsheet":

□ Step 1: Identify Problem File
   - Review log file for last processed file
   - Problem file: _______________________________________

□ Step 2: Test File Manually
   - Navigate to file location
   - Try to open in Excel
   - File opens: _____
   - If not, error: ______________________________________

□ Step 3: Check File Format
   - File extension: _____ (.xlsx/.xls/.csv)
   - Valid extension: _____
   - File size: ____KB (Normal: 50-500KB)

□ Step 4: Check File Content
   - Open file in Excel
   - Has headers: _____
   - Has data rows: _____ (Count: ____)
   - Status column exists: _____
   - Status column name matches config: _____
   - No password protection: _____

□ Step 5: Check for Corruption
   - Try to save file as new name
   - Can save: _____
   - If cannot save: File is corrupted

□ Step 6: Resolution
   IF file corrupted:
     - Move to Archive folder
     - Request new file from source bot
     - Document in incident log
   
   IF file format issue:
     - Convert to .xlsx format
     - Save and retry

□ Step 7: Retry Bot
   - Trigger bot manually
   - Result: _____ (Success/Failed)

IF STILL FAILING: Escalate to L2
```

#### 5.5 Configuration File Error
```
IF Error contains "Config" or occurs at start:

□ Step 1: Verify Config File Exists
   - Navigate to: C:\RPAProcesses\Report_Bot\Config
   - Bot_Config.xlsx exists: _____
   - File size > 0: _____

□ Step 2: Open and Validate Config
   - Open Bot_Config.xlsx
   - Sheet1 exists: _____
   - General_Config sheet exists: _____
   - No #REF! errors: _____
   - No #VALUE! errors: _____
   - No blank required fields: _____

□ Step 3: Validate Required Columns (Sheet1)
   - BotName column exists: _____
   - FolderPath column exists: _____
   - StatusColumn column exists: _____
   - LogicType column exists: _____
   - Keyword column exists: _____

□ Step 4: Validate General_Config
   - Sharepoint Path populated: _____
   - Email Addresses populated: _____
   - Main File Path populated: _____

□ Step 5: Test Paths in Config
   - Test each FolderPath: _____
   - Test SharePoint path: _____
   - Test Main File Path: _____
   - All paths accessible: _____

□ Step 6: Restore from Backup (if needed)
   - Locate backup config file
   - Copy to Config folder
   - Verify backup is valid

□ Step 7: Retry Bot
   - Trigger bot manually
   - Result: _____ (Success/Failed)

IF STILL FAILING: Escalate to L2
```

#### 5.6 System Resource Issue
```
IF Error contains "memory" or "timeout" or bot hangs:

□ Step 1: Check System Resources
   - Open Task Manager
   - CPU usage: ____% (High if >90%)
   - Memory usage: ____% (High if >90%)
   - Disk usage: ____% (High if >90%)

□ Step 2: Identify Resource Hog
   - Sort by CPU/Memory
   - Top process: _____________________ (____%)
   - Is it expected: _____

□ Step 3: Check for Hung Excel Processes
   - Filter Task Manager by "Excel"
   - Excel process count: _____
   - Any "Not Responding": _____

□ Step 4: Clean Up Processes
   - Kill all Excel processes:
     taskkill /t /IM EXCEL.EXE /f
   - Kill any hung bot processes
   - Wait 30 seconds

□ Step 5: Check Disk Space
   - C: drive free space: ____GB
   - If <1GB: Clean up temp files
   - After cleanup: ____GB

□ Step 6: Restart Services (if needed)
   - Restart Automation Anywhere Bot Agent
   - Wait 2 minutes for service to start

□ Step 7: Retry Bot
   - Trigger bot manually
   - Monitor resource usage
   - Result: _____ (Success/Failed)

IF STILL FAILING: Escalate to L2
```

**Troubleshooting Summary:**
```
Issue Category: __________________________________________
Root Cause: ______________________________________________
Resolution Applied: ______________________________________
Retry Result: _____ (Success/Failed)
Time to Resolve: _____ minutes
Escalated: _____ (Yes/No)
```

---

## 6. Common Issues & Resolutions

### Quick Reference Guide

#### Issue 1: "Unable to connect to Outlook"
**Symptoms:** Bot fails at email connection step  
**Quick Fix:**
```
1. Open Outlook manually on bot runner machine
2. Wait 60 seconds for full load
3. Verify "Report" folder is visible
4. Retry bot execution
```
**Prevention:** Keep Outlook running 24/7 on bot runner

---

#### Issue 2: "No emails found in Report folder"
**Symptoms:** Bot completes but no files processed  
**Quick Fix:**
```
1. Open Outlook → Report folder
2. Check date filter: Yesterday's date
3. Verify emails exist with correct keywords
4. If emails missing: Contact source bot owners
5. If emails in wrong folder: Move to Report folder
6. Retry bot execution
```
**Prevention:** Monitor source bots daily

---

#### Issue 3: "SharePoint file access denied"
**Symptoms:** Bot fails during SharePoint copy  
**Quick Fix:**
```
1. Open File Explorer
2. Navigate to SharePoint path
3. Check if file is locked (Properties → Details)
4. If locked: Contact user to close file
5. Verify bot runner account has permissions
6. Retry bot execution
```
**Prevention:** Schedule bot during off-hours

---

#### Issue 4: "Excel file corrupted"
**Symptoms:** Bot fails when opening specific file  
**Quick Fix:**
```
1. Identify problem file from log
2. Try to open manually in Excel
3. If cannot open: Move to Archive
4. Request new file from source bot
5. Place new file in Input folder
6. Retry bot execution
```
**Prevention:** Implement file validation in source bots

---

#### Issue 5: "Config file not found"
**Symptoms:** Bot fails immediately at start  
**Quick Fix:**
```
1. Navigate to: C:\RPAProcesses\Report_Bot\Config
2. Check if Bot_Config.xlsx exists
3. If missing: Restore from backup location
4. Verify file can be opened
5. Retry bot execution
```
**Prevention:** Daily backup of config file

---

#### Issue 6: "Disk space full"
**Symptoms:** Bot fails when creating files  
**Quick Fix:**
```
1. Check C: drive free space
2. If <1GB: Clean up temp files
   - Delete: C:\Windows\Temp\*
   - Delete: C:\Users\[User]\AppData\Local\Temp\*
3. Archive old log files (>30 days)
4. Archive old daily reports (>90 days)
5. Retry bot execution
```
**Prevention:** Weekly disk cleanup schedule

---

#### Issue 7: "Retry count exceeded (SharePoint)"
**Symptoms:** Bot fails after 10 retry attempts  
**Quick Fix:**
```
1. Check network connectivity to SharePoint
2. Ping SharePoint server
3. Check if SharePoint site is down
4. Verify file is not locked
5. Check bot runner account permissions
6. If all OK: Wait 5 minutes and retry
```
**Prevention:** Monitor SharePoint availability

---

#### Issue 8: "Wrong data counts in report"
**Symptoms:** Numbers don't match source files  
**Quick Fix:**
```
1. Open input file for affected bot
2. Manually count Success/Exception/Failure
3. Compare with daily report
4. Check StatusColumn name in config
5. Verify LogicType is correct
6. If config wrong: Update and rerun
7. If logic issue: Escalate to L2
```
**Prevention:** Monthly config validation

---

## 7. Emergency Procedures

### Emergency Scenario 1: Bot Stuck/Hanging
**Indicators:** Bot running >60 minutes, no log updates  
**Immediate Actions:**
```
□ Step 1: Confirm Bot is Stuck
   - Check Control Room: Status = "Running"
   - Check log file: No updates in last 10 minutes
   - Check Task Manager: Excel processes hung

□ Step 2: Stop Bot Execution
   - Control Room → Running Bots → Report_Main
   - Click "Stop" button
   - Wait 30 seconds
   - Verify status changed to "Stopped"

□ Step 3: Clean Up Processes
   - Open Task Manager on bot runner
   - Kill all Excel processes:
     taskkill /t /IM EXCEL.EXE /f
   - Kill any hung AA processes

□ Step 4: Document State
   - Note: Time stuck, last log entry, system state
   - Take screenshot of Task Manager
   - Save log file with "_STUCK" suffix

□ Step 5: Restart Bot
   - Wait 2 minutes
   - Trigger bot manually
   - Monitor closely for first 10 minutes

□ Step 6: Escalate if Repeats
   - If stuck again: Escalate to L2 immediately
   - Provide: Log files, screenshots, timing details
```

---

### Emergency Scenario 2: Critical Data Error Detected
**Indicators:** Stakeholder reports wrong numbers  
**Immediate Actions:**
```
□ Step 1: Verify Error
   - Open daily report file
   - Open source input files
   - Manually verify counts for reported bot
   - Confirm discrepancy: _____

□ Step 2: Assess Impact
   - Number of bots affected: _____
   - Magnitude of error: _____%
   - Critical decision impacted: _____ (Yes/No)

□ Step 3: Send Correction Notice
   - Email stakeholders immediately
   - Subject: "URGENT: Daily Report Correction Required"
   - Explain: Which bots affected, correct numbers
   - Timeline for corrected report: _____

□ Step 4: Identify Root Cause
   - Check config file for changes
   - Check input file format changes
   - Check logic type correctness
   - Root cause: _____________________________________

□ Step 5: Generate Corrected Report
   - Fix root cause (config/input files)
   - Rerun bot manually
   - Validate output carefully
   - Send corrected report to stakeholders

□ Step 6: Escalate to L2
   - Create incident ticket
   - Provide: Original report, corrected report, root cause
   - Request: Code review if logic issue
```

---

### Emergency Scenario 3: SharePoint Site Down
**Indicators:** Cannot access SharePoint, network error  
**Immediate Actions:**
```
□ Step 1: Confirm SharePoint Down
   - Test SharePoint URL in browser
   - Ping SharePoint server
   - Check with IT: Site status
   - Confirmed down: _____ (Yes/No)

□ Step 2: Notify Stakeholders
   - Email: "Daily Report Delayed - SharePoint Unavailable"
   - Estimated resolution time: _____
   - Alternative: Manual report if needed

□ Step 3: Prepare Workaround
   - Generate daily report locally (bot will do this)
   - Save to: C:\RPAProcesses\Report_Bot\Daily_Report
   - Email daily report directly to stakeholders
   - Note: Master file will be updated when SharePoint returns

□ Step 4: Monitor SharePoint Status
   - Check every 30 minutes
   - When available: _____

□ Step 5: Update Master File
   - Once SharePoint available:
   - Manually run bot OR
   - Manually copy daily data to master file
   - Verify data integrity

□ Step 6: Document Incident
   - Downtime duration: _____
   - Impact: _____
   - Resolution: _____
```

---

## 8. Escalation Procedures

### When to Escalate to L2

#### Immediate Escalation (Critical)
```
Escalate IMMEDIATELY if:
□ Data accuracy issues (wrong counts in report)
□ Bot fails 3 consecutive times with same error
□ Security issue detected (unauthorized access)
□ Code change required (new bot, new logic)
□ Application structural change (Outlook, SharePoint, Excel)
```

#### Escalation After Troubleshooting (High Priority)
```
Escalate AFTER L1 troubleshooting if:
□ Issue persists after following runbook steps
□ Root cause unclear after 30 minutes investigation
□ Requires configuration file structure change
□ Requires new logic type implementation
□ Performance degradation (>60 minutes runtime)
```

#### Scheduled Escalation (Medium Priority)
```
Escalate DURING business hours if:
□ Enhancement request from stakeholders
□ New bot needs to be added to reporting
□ Config file optimization needed
□ Recurring minor issues (>3 times per week)
```

---

### Escalation Process

#### Step 1: Gather Information
```
Before escalating, collect:
□ Bot run ID from Control Room
□ Complete log file (latest)
□ Screenshot of error from Control Room
□ Config file (Bot_Config.xlsx)
□ Sample input files (if data issue)
□ List of L1 troubleshooting steps performed
□ Exact error message and line number
□ Time of failure and duration
□ System resource status at time of failure
```

#### Step 2: Create Escalation Ticket
```
Ticket Template:

Title: [Bot Name] - [Issue Category] - [Date]
Example: Report_Main - SharePoint Access Failure - 2026-06-15

Priority: _____ (Critical/High/Medium/Low)

Description:
- Issue: _____________________________________________
- First Occurrence: __________________________________
- Frequency: _________________________________________
- Impact: ____________________________________________
- Business Impact: ___________________________________

L1 Troubleshooting Performed:
1. ___________________________________________________
2. ___________________________________________________
3. ___________________________________________________

Attachments:
- Log file: __________________________________________
- Config file: _______________________________________
- Screenshots: _______________________________________
- Input files: _______________________________________

Requested Action:
___________________________________________________
___________________________________________________
```

#### Step 3: Notify L2 Team
```
□ Create ticket in ServiceNow
   - Category: RPA - Support
   - Subcategory: Bot Failure
   - Assignment Group: RPA L2 Support

□ Send email notification
   - To: rpa.l2.support@company.com
   - Subject: [ESCALATION] Report_Main - [Issue]
   - Include: Ticket number, summary, urgency

□ If Critical: Call L2 on-call
   - Phone: [L2 On-Call Number]
   - Provide: Ticket number, brief summary
```

#### Step 4: Handover to L2
```
□ Provide access to bot runner machine
   - Credentials: [Service Account]
   - Remote access: [RDP/VPN details]

□ Brief L2 engineer
   - Explain issue and troubleshooting done
   - Show log files and error location
   - Demonstrate issue if reproducible

□ Remain available for questions
   - L2 may need additional information
   - Be ready to test fixes
```

#### Step 5: Follow Up
```
□ Monitor ticket status
   - Check every 2 hours for updates
   - Respond to L2 questions promptly

□ Test resolution
   - When L2 provides fix, test immediately
   - Validate bot runs successfully
   - Confirm data accuracy

□ Close ticket
   - Verify issue fully resolved
   - Document resolution in ticket
   - Update runbook if new procedure learned
```

---

### L2 Contact Information

**L2 Support Team:**
- Email: rpa.l2.support@company.com
- Phone: [L2 Support Number]
- On-Call: [L2 On-Call Number]
- Hours: 24/7 for Critical issues

**RPA Development Team:**
- Email: rpa.dev@company.com
- Phone: [Dev Team Number]
- Hours: Mon-Fri 9AM-5PM

**Escalation Matrix:**

| Issue Severity | Response Time | Contact |
|----------------|---------------|---------|
| Critical | 15 minutes | L2 On-Call |
| High | 2 hours | L2 Support Email |
| Medium | 4 hours | L2 Support Email |
| Low | Next business day | L2 Support Email |

---

## Appendix A: Checklist Templates

### Daily Execution Checklist
```
Date: _______________  Operator: _______________

Pre-Execution:
□ Health check completed
□ Outlook running and connected
□ SharePoint accessible
□ Config file validated
□ Input emails verified

Execution:
□ Bot started at: _____
□ Monitoring performed every 5 minutes
□ No errors observed during run
□ Bot completed at: _____
□ Duration: _____ minutes (Normal: 15-30)

Post-Execution:
□ Daily report file created
□ Master file updated
□ Email sent to stakeholders
□ Data spot-check performed
□ All validations passed

Issues:
□ No issues
□ Issues found and resolved (details below)
□ Issues escalated to L2 (ticket: _____)

Notes:
_______________________________________________________
_______________________________________________________
```

---

### Weekly Maintenance Checklist
```
Week of: _______________  Operator: _______________

System Health:
□ Bot runner machine rebooted
□ Disk cleanup performed (C: drive)
□ Old log files archived (>30 days)
□ Old daily reports archived (>90 days)
□ Config file backed up

Performance Review:
□ Average execution time: _____ minutes
□ Success rate: _____%
□ Number of failures: _____
□ Common issues identified: _________________________

Preventive Actions:
□ Outlook profile verified
□ SharePoint connectivity tested
□ Excel processes cleaned up
□ Bot agent service restarted

Documentation:
□ Runbook updated with new issues/resolutions
□ Incident log reviewed
□ Escalations reviewed with L2

Notes:
_______________________________________________________
_______________________________________________________
```

---

## Appendix B: Quick Command Reference

### PowerShell Commands
```powershell
# Check bot runner processes
Get-Process | Where-Object {$_.ProcessName -like "*Automation*"}

# Kill Excel processes
taskkill /t /IM EXCEL.EXE /f

# Check disk space
Get-PSDrive C | Select-Object Used,Free

# Test SharePoint connectivity
Test-Path "\\sharepoint\path\to\file.xlsx"

# View latest log file
Get-Content "C:\RPAProcesses\Report_Bot\Audit_logs\Log_file*.txt" -Tail 50

# Search for errors in logs
Select-String -Path "C:\RPAProcesses\Report_Bot\Audit_logs\*.txt" -Pattern "error|failed"

# Check file lock status
Get-Process | Where-Object {$_.MainWindowTitle -like "*Master_Report*"}

# Restart AA Bot Agent service
Restart-Service "Automation Anywhere Bot Agent"
```

---

## Appendix C: Contact Directory

### Support Contacts
| Role | Name | Email | Phone | Hours |
|------|------|-------|-------|-------|
| L1 Support Lead | [Name] | [Email] | [Phone] | 24/7 |
| L2 Support Lead | [Name] | [Email] | [Phone] | 24/7 |
| RPA Developer | [Name] | [Email] | [Phone] | Mon-Fri 9-5 |
| Bot Owner | [Name] | [Email] | [Phone] | Mon-Fri 9-5 |

### Stakeholder Contacts
| Role | Name | Email | Phone |
|------|------|-------|-------|
| Report Recipient | [Name] | [Email] | [Phone] |
| Business Owner | [Name] | [Email] | [Phone] |
| IT Support | [Name] | [Email] | [Phone] |

---

## Document Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | June 2026 | RPA Support Team | Initial runbook creation |

---

**Document Owner:** RPA Support Team  
**Review Frequency:** Monthly  
**Next Review Date:** [Date]  
**Approval:** [Manager Name]