# L1 → L2 Support Transition Guide
## Carhartt Reporting Bot - Complete Knowledge Transfer Document

---

## 📋 Document Purpose

This guide helps new L1 support resources understand the Carhartt Reporting Bot and gradually build L2-level knowledge for troubleshooting and maintenance.

**Target Audience:** New L1 support team members, L1 resources transitioning to L2, Support team onboarding

**How to Use This Guide:**
1. Start with Section 1-6 for basic understanding (L1 level)
2. Progress to Section 7-11 for deeper knowledge (L2 level)
3. Use Section 12-13 as quick reference during incidents
4. Review Section 14-15 for continuous improvement

---

## 1. Bot Overview (Simple Explanation)

### What Does This Bot Do?

**In Simple Terms:**
This Reporting Bot is like a **manager robot** that collects daily reports from 5-10 other robots, counts their successes and failures, creates one combined summary report, saves it in SharePoint, and emails it to the team.

**Real-World Analogy:** Like a teacher collecting homework from 10 students, checking each one, and creating a summary report for the principal.

### Why Does This Automation Exist?

**Before Automation:** Support analyst spent 2-3 hours every morning manually collecting and consolidating reports.

**After Automation:** Bot completes the same work in 15-30 minutes (90% faster) with zero errors.

### End-to-End Process Summary

```
6:00 AM → Bot starts
6:02 AM → Connects to Outlook, downloads reports
6:05 AM → Processes each bot's report
6:20 AM → Updates SharePoint
6:25 AM → Sends email to team
6:30 AM → Bot finishes
```

---

## 2. High-Level Process Flow

### 8-Step Process

**STEP 1: INITIALIZE** (2 min) - Kill stuck Excel, calculate dates, create folders
**STEP 2: LOAD CONFIG** (1 min) - Read Bot_Config.xlsx, clean old files
**STEP 3: CONNECT OUTLOOK** (30 sec) - Open Outlook, wait for sync
**STEP 4: DOWNLOAD FILES** (2 min) - Get yesterday's email attachments
**STEP 5: PROCESS REPORTS** (10-15 min) - Count transactions for each bot
**STEP 6: CONSOLIDATE** (5 min) - Combine with historical data
**STEP 7: UPDATE SHAREPOINT** (5 min) - Upload master file with retry
**STEP 8: SEND NOTIFICATIONS** (1 min) - Email daily report to stakeholders

**Total Time:** 20-30 minutes

---

## 3. Component & Code Structure

### Main Components

**👔 Report_Main (The Manager)** - Coordinates everything, handles Outlook/SharePoint, sends emails
**👷 SubTask_Report (The Worker)** - Opens Excel files, counts rows, calculates metrics
**📋 Bot_Config.xlsx (Instruction Manual)** - Lists bots to process, email addresses, SharePoint location
**📊 Master.xlsx (History Book)** - Stored in SharePoint, contains all historical data

### How They Work Together

```
Report_Main → Reads Bot_Config.xlsx
           → Calls SubTask_Report for each bot
           → SubTask processes files and returns counts
           → Report_Main consolidates and updates SharePoint
```

---

## 4. Applications & Integrations

**📧 OUTLOOK** - Reads emails from "Report" folder, downloads attachments, sends notifications
**📁 SHAREPOINT** - Reads/writes master Excel file via UNC path (\\sharepoint\...)
**📊 EXCEL** - Opens .xlsx files, reads data, writes results
**💾 FILE SYSTEM** - Creates folders, copies files, writes logs

**Important:** No web scraping, APIs, or databases - only desktop apps and file operations!

---

## 5. Key Logic & Decision Points

### 6 Logic Types (How Bot Counts Transactions)

**1. Status** - Check Status column: "exception" → Exception, "success" → Success, else → Failure
**2. KeywordCheck** - "parked" → Success, else → Exception
**3. CMT** - Comment not empty → Success, else → Exception
**4. HeaderPR** - Loop="H" AND Remark="Success" → Success
**5. RTLStatus** - Status contains "released" → Success
**6. CreditRisk** - Status contains output path → Success

---

## 6. Input, Output & Data Handling

### Inputs
- **Config File:** C:\RPAProcesses\Report_Bot\Config\Bot_Config.xlsx
- **Email Reports:** Outlook "Report" folder (yesterday's emails)
- **Master File:** \\sharepoint\sites\RPA\Reports\Master.xlsx

### Outputs
- **Daily Summary:** C:\RPAProcesses\Report_Bot\Daily_Report\14-Jun.xlsx
- **Updated Master:** \\sharepoint\sites\RPA\Reports\Master.xlsx (with new data)
- **Execution Log:** C:\RPAProcesses\Report_Bot\Audit_logs\Log_file140626_07_15.txt
- **Email Notifications:** Sent to support team with attachments

---

## 7. Variables & Configuration

### Key Variables
- **BotName** - Which bot we're processing
- **FolderPath** - Where to find input files
- **StatusColumn** - Which column to check
- **LogicType** - Which counting rule to use
- **Volume/Success/Exception/Failure** - Transaction counters

### Configuration File
**Location:** C:\RPAProcesses\Report_Bot\Config\Bot_Config.xlsx
**Sheet 1:** Bot Configuration (bot settings)
**Sheet 2:** General_Config (SharePoint path, email addresses)

---

## 8. Error Handling & Recovery

### Three Levels
**Level 1: Global Handler** - Catches any main bot error → Log, send failure email, stop
**Level 2: Retry Logic** - SharePoint failures → Retry 10 times with 5-second delay
**Level 3: File Handler** - Individual file errors → Log, skip file, continue

---

## 9. Logging & Monitoring

### Log Locations
- **Execution Logs:** C:\RPAProcesses\Report_Bot\Audit_logs\
- **Control Room:** A360 web interface → Bot Activity
- **Daily Reports:** C:\RPAProcesses\Report_Bot\Daily_Report\

### How to Track
**Method 1:** Check for "Daily Status Report" email at 6:30 AM
**Method 2:** Check Control Room for "Report_Main" status
**Method 3:** Open latest log file and check last line

---

## 10. L1 Support – Quick Troubleshooting Guide ✅

### L1 Checklist (Follow Step-by-Step)

#### ✅ STEP 1: Verify Bot Status (2 min)
1. Log into A360 Control Room
2. Go to: Automation → Activity → Bot Activity
3. Find "Report_Main" (sort by date)
4. Check status: Success ✅ or Failed ❌

#### ✅ STEP 2: Validate Input Files (3 min)
1. Open Outlook → "Report" folder
2. Check for yesterday's emails with attachments
3. Verify file names match expected pattern

#### ✅ STEP 3: Verify Credentials (1 min)
1. Check bot runner machine is online
2. Verify Outlook is running
3. Test SharePoint access: \\sharepoint\sites\RPA\Reports\

#### ✅ STEP 4: Check Applications (2 min)
1. Outlook: Open and responding?
2. Excel: Try opening a test file
3. SharePoint: Can you access the folder?
4. Network: Ping SharePoint server

#### ✅ STEP 5: Review Errors (5 min)
1. Open latest log file in Audit_logs folder
2. Look for error messages
3. Check Control Room error details
4. Screenshot errors for escalation

#### ✅ STEP 6: Try Quick Fixes (5 min)

**Fix 1: Restart Outlook**
```
1. Close Outlook on bot runner
2. Wait 10 seconds
3. Open Outlook, wait for sync
4. Rerun bot
```

**Fix 2: Kill Excel**
```
1. Open Task Manager
2. End all EXCEL.EXE processes
3. Rerun bot
```

**Fix 3: Clear Input Folders**
```
1. Navigate to bot input folders
2. Move old files to archive
3. Rerun bot
```

#### ✅ STEP 7: Rerun Bot (2 min)
1. Control Room → Bots → Report_Bot → Report_Main
2. Click "Run" → "Run Now"
3. Monitor execution for 5 minutes

#### ✅ STEP 8: Verify Success (3 min)
1. Check for daily status email
2. Verify daily report file created
3. Check SharePoint updated
4. Review log shows "Execution completed"

---

## 11. L2 Support – Deep Analysis Guide ✅

### When to Escalate from L1 to L2

**Escalate if:**
- Bot fails 3+ times with same error
- Data accuracy issues reported
- Configuration changes needed
- Logic changes required
- Performance degradation (>1 hour)

### L2 Deep Dive Analysis

#### 🔍 STEP 1: Analyze Logs (10 min)
- Search for "Error" or "Exception"
- Check timestamps for delays
- Compare with successful runs
- Look for retry patterns

#### 🔍 STEP 2: Debug Bot Code (15 min)
- Open bot in Bot Editor
- Review error line number
- Check logic at failure point
- Verify variable values

#### 🔍 STEP 3: Test with Sample Data (20 min)
- Copy one bot's input file
- Run in debug mode
- Step through execution
- Verify counts manually

#### 🔍 STEP 4: Check Data Quality (15 min)
- Open input Excel files
- Check for missing columns, blank rows
- Validate against expected format
- Look for special characters

#### 🔍 STEP 5: Review Configuration (10 min)
- Validate Bot_Config.xlsx
- Check folder paths exist
- Verify status column names
- Validate logic types

#### 🔍 STEP 6: Performance Analysis (10 min)
- Review log timestamps
- Calculate time per step
- Compare with baseline (20-30 min normal)
- Identify bottlenecks

### L2 Resolution Actions

**Action 1: Fix Configuration** - Backup, make changes, test, deploy
**Action 2: Update Bot Logic** - Edit in Bot Editor, test, get approval, deploy
**Action 3: Coordinate with Source Bots** - Contact bot teams, validate formats
**Action 4: Optimize Performance** - Identify slow operations, implement improvements

---

## 12. Common Failure Scenarios

### Scenario 1: Config File Missing
**Symptoms:** Bot fails immediately, "File not found" error
**L1 Fix:** Check file exists, restore from backup, rerun
**L2 Fix:** Verify permissions, check file path in code, implement validation

### Scenario 2: No Input Files
**Symptoms:** Zero counts for all bots, no errors
**L1 Fix:** Check Outlook "Report" folder, verify source bots ran
**L2 Fix:** Analyze email filters, verify keywords, add zero-file alerts

### Scenario 3: SharePoint Failure
**Symptoms:** Multiple retry attempts, all exhausted
**L1 Fix:** Check SharePoint availability, test manual access, rerun
**L2 Fix:** Verify permissions, check UNC path, increase retries, use DFS

### Scenario 4: Excel File Corrupted
**Symptoms:** Fails on specific bot, file won't open
**L1 Fix:** Try opening manually, contact source bot team, request resend
**L2 Fix:** Implement file validation, add repair logic, work with source team

### Scenario 5: Outlook Not Responding
**Symptoms:** Bot hangs at Outlook connection, no progress
**L1 Fix:** Kill Outlook, restart, wait for sync, rerun
**L2 Fix:** Recreate profile, optimize mailbox, add timeout, consider EWS

### Scenario 6: Data Count Mismatch
**Symptoms:** Stakeholders report incorrect counts
**L1 Fix:** Count manually, compare with report, document difference
**L2 Fix:** Analyze file structure, review logic, test manually, fix config

---

## 13. Escalation Guidelines

### L1 → L2 Escalation
**Escalate if:** Bot fails 3+ times, data issues, config changes needed, logic modifications required

### L2 → L3/Dev Escalation
**Escalate if:** Code changes required, new logic type needed, architecture changes, security issues

### Escalation Template
```
Subject: [URGENT] Carhartt Reporting Bot - [Issue Type]
Priority: P1/P2/P3/P4
Issue: What happened? When? How many times?
Troubleshooting: L1 steps completed, results
Attachments: Log file, screenshots, error messages
Requested Action: What needs fixing? Urgency? Impact?
```

---

## 14. Knowledge Transition Tips

### Week 1: Foundation (L1)
- Read Sections 1-6
- Shadow experienced analyst
- Observe bot execution
- Practice daily monitoring

### Week 2: L1 Proficiency
- Practice troubleshooting checklist
- Simulate failures in dev
- Study configuration file
- Monitor independently

### Week 3-4: L2 Preparation
- Read Sections 7-11
- Open bot in Bot Editor
- Study error handling
- Practice advanced troubleshooting

### Month 2: L2 Readiness
- Handle 5+ incidents independently
- Perform 2+ config updates
- Add 1 new bot
- Pass L2 assessment

---

## 15. Improvement Opportunities

### Logging Improvements
- Add structured logging (INFO/WARN/ERROR levels)
- Include correlation IDs
- Send to central logging system
- Create dashboards

### Error Handling Enhancements
- Intelligent retry with exponential backoff
- Graceful degradation (continue with other bots)
- Self-healing (auto-restart Outlook)
- Better error messages with resolution steps

### Performance Optimizations
- Parallel processing (multiple bots simultaneously)
- Caching (config file, Outlook connection)
- Use CSV instead of XLSX
- Smart scheduling (off-peak hours)

### Reusability Suggestions
- Generic reporting framework
- Plugin architecture for logic types
- Template-based reports
- API-based reporting

### Monitoring & Alerting
- Real-time dashboard
- Proactive alerts (bot not started, execution too long)
- Pre-execution health checks
- Automated weekly/monthly reports

### Data Quality Improvements
- Input validation (file structure, columns, data types)
- Data quality checks (compare with historical averages)
- Reconciliation with source systems
- Quality metrics tracking

---

## 📚 Quick Reference Card

### Emergency Contacts
- **L1 Support:** support@company.com
- **L2 Support:** l2support@company.com
- **L3/Dev Team:** devteam@company.com

### Key Locations
```
Config: C:\RPAProcesses\Report_Bot\Config\Bot_Config.xlsx
Logs: C:\RPAProcesses\Report_Bot\Audit_logs\
Reports: C:\RPAProcesses\Report_Bot\Daily_Report\
SharePoint: \\sharepoint\sites\RPA\Reports\Master.xlsx
```

### Common Commands
```powershell
# Kill Excel
taskkill /F /IM EXCEL.EXE

# Check SharePoint
Test-Path "\\sharepoint\sites\RPA\Reports\Master.xlsx"

# View Latest Log
Get-Content "C:\RPAProcesses\Report_Bot\Audit_logs\*.txt" | Select-Object -Last 50
```

### Normal Execution Times
- **Total:** 20-30 minutes
- **Initialization:** 2 minutes
- **Outlook:** 30 seconds
- **Per bot:** 2-3 minutes
- **SharePoint:** 5 minutes

### Success Criteria
- ✅ Daily email received by 6:30 AM
- ✅ All bots in daily report
- ✅ Counts are non-zero and reasonable
- ✅ SharePoint updated
- ✅ Log shows "Execution completed"

---

## 📖 Glossary

**A360** - Automation Anywhere 360, cloud-native RPA platform
**Bot Runner** - Machine where bot executes
**Control Room** - A360 web interface for managing bots
**DataTable** - In-memory table structure for data processing
**Logic Type** - Rule for counting transactions (Status, KeywordCheck, etc.)
**Session** - Named connection to application (Excel, Outlook)
**SubTask** - Reusable bot called by main bot
**UNC Path** - Network file path (\\server\share\file)

---

**Document Version:** 1.0  
**Last Updated:** June 2026  
**Owner:** RPA Support Team  
**Review Frequency:** Quarterly

---

**END OF DOCUMENT**