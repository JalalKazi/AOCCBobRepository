# Carhartt Reporting Bot - L1/L2 Support Documentation

**Developer:** Anima Lal  
**Platform:** Automation Anywhere A360  
**Last Updated:** June 2026

---

## 1. Bot Overview

### Purpose (Business Use Case)
The Carhartt Reporting Bot automates the daily collection and consolidation of RPA bot execution reports. It:
- Retrieves bot performance reports from Outlook emails
- Processes Excel files to calculate success/failure metrics
- Consolidates data into a daily summary report
- Updates a master SharePoint file with historical data
- Sends automated status emails to stakeholders

**Business Value:** Eliminates 2-3 hours of manual daily reporting effort, provides consistent metrics tracking, and ensures timely visibility into bot performance.

### High-Level Process Flow
1. **Initialize** → Kill Excel processes, calculate report date (yesterday), create necessary folders
2. **Setup** → Open configuration file, create input/archive folders, clean old files
3. **Connect Email** → Connect to Outlook, wait 20 seconds for sync
4. **Download Reports** → Fetch Excel attachments from "Report" folder based on keywords
5. **Process Each Bot** → Call SubTask_Report for each configured bot to analyze metrics
6. **Consolidate** → Copy SharePoint master file, merge daily data, update SharePoint
7. **Notify** → Send daily summary email with attachment to stakeholders

### Trigger Mechanism
- **Scheduled Execution** - Runs daily (typically early morning after all bots complete)
- **Manual Trigger** - Can be run on-demand from Control Room
- **No API/Event Triggers** - Pure time-based scheduling

### Visual Process Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CARHARTT REPORTING BOT                              │
│                            (Report_Main)                                     │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────────────┐
    │  START: Scheduled Trigger (Daily)                                │
    └────────────────────────┬─────────────────────────────────────────┘
                             │
                             ▼
    ┌────────────────────────────────────────────────────────────────┐
    │  PHASE 1: INITIALIZATION                                       │
    │  • Kill Excel processes (taskkill)                             │
    │  • Calculate dates (yesterday = report date)                   │
    │  • Create folder structure                                     │
    │  • Create daily Excel file with headers                        │
    │  • Initialize log file                                         │
    └────────────────────────┬───────────────────────────────────────┘
                             │
                             ▼
    ┌────────────────────────────────────────────────────────────────┐
    │  PHASE 2: CONFIGURATION LOADING                                │
    │  • Open Bot_Config.xlsx                                        │
    │  • Read bot configurations (Sheet1)                            │
    │  • Read general settings (General_Config)                      │
    │  • Create input/archive folders per bot                        │
    │  • Clean old files (move to archive)                           │
    └────────────────────────┬───────────────────────────────────────┘
                             │
                             ▼
    ┌────────────────────────────────────────────────────────────────┐
    │  PHASE 3: EMAIL PROCESSING                                     │
    │  • Connect to Outlook                                          │
    │  • Wait 20 seconds for sync                                    │
    │  • Read emails from "Report" folder (yesterday's date)         │
    │  ┌──────────────────────────────────────────────────────────┐ │
    │  │  FOR EACH Email:                                         │ │
    │  │    FOR EACH Bot Config:                                  │ │
    │  │      IF subject contains Keyword:                        │ │
    │  │        → Save attachment to FolderPath                   │ │
    │  │      IF subject = "Error-Cash App Remittance":           │ │
    │  │        → Extract error message                           │ │
    │  │        → Increment MailFailure counter                   │ │
    │  └──────────────────────────────────────────────────────────┘ │
    └────────────────────────┬───────────────────────────────────────┘
                             │
                             ▼
    ┌────────────────────────────────────────────────────────────────┐
    │  PHASE 4: DATA PROCESSING                                      │
    │  ┌──────────────────────────────────────────────────────────┐ │
    │  │  FOR EACH Bot in Config:                                 │ │
    │  │    ┌──────────────────────────────────────────────────┐ │ │
    │  │    │  CALL SubTask_Report                             │ │ │
    │  │    │  • Pass: BotName, FolderPath, StatusColumn,      │ │ │
    │  │    │          LogicType, CheckColumn, FileKeyword     │ │ │
    │  │    │  ┌────────────────────────────────────────────┐ │ │ │
    │  │    │  │  SubTask Processing:                       │ │ │ │
    │  │    │  │  • Loop through files in FolderPath        │ │ │ │
    │  │    │  │  • Open Excel file                         │ │ │ │
    │  │    │  │  • Read data into DataTable                │ │ │ │
    │  │    │  │  • FOR EACH Row:                           │ │ │ │
    │  │    │  │    - Apply LogicType rules                 │ │ │ │
    │  │    │  │    - Count: Volume, Success, Exception,    │ │ │ │
    │  │    │  │             Failure                         │ │ │ │
    │  │    │  │  • Close Excel file                        │ │ │ │
    │  │    │  │  • RETURN counts                           │ │ │ │
    │  │    │  └────────────────────────────────────────────┘ │ │ │
    │  │    │  • Write results to daily Excel file            │ │ │
    │  │    └──────────────────────────────────────────────────┘ │ │
    │  └──────────────────────────────────────────────────────────┘ │
    └────────────────────────┬───────────────────────────────────────┘
                             │
                             ▼
    ┌────────────────────────────────────────────────────────────────┐
    │  PHASE 5: SHAREPOINT SYNCHRONIZATION                           │
    │  ┌──────────────────────────────────────────────────────────┐ │
    │  │  COPY FROM SharePoint (with retry):                      │ │
    │  │  • Kill Excel processes                                  │ │
    │  │  • Copy master file from SharePoint to Main_Folder       │ │
    │  │  • Retry up to 10 times if failed (5-sec delay)          │ │
    │  └──────────────────────────────────────────────────────────┘ │
    │                           │                                    │
    │                           ▼                                    │
    │  ┌──────────────────────────────────────────────────────────┐ │
    │  │  MERGE DATA:                                             │ │
    │  │  • Open daily file (today's summary)                     │ │
    │  │  • Open main file (master historical)                    │ │
    │  │  • Get row count in main file                            │ │
    │  │  • FOR EACH row in daily file:                           │ │
    │  │    → Append to main file (Date, Bot, Volume, Success,    │ │
    │  │                           Exception, Failure, Remarks)    │ │
    │  │  • Close both files with save                            │ │
    │  └──────────────────────────────────────────────────────────┘ │
    │                           │                                    │
    │                           ▼                                    │
    │  ┌──────────────────────────────────────────────────────────┐ │
    │  │  COPY TO SharePoint (with retry):                        │ │
    │  │  • Kill Excel processes                                  │ │
    │  │  • Copy updated main file back to SharePoint             │ │
    │  │  • Create archive copy with timestamp                    │ │
    │  │  • Retry up to 10 times if failed (5-sec delay)          │ │
    │  └──────────────────────────────────────────────────────────┘ │
    └────────────────────────┬───────────────────────────────────────┘
                             │
                             ▼
    ┌────────────────────────────────────────────────────────────────┐
    │  PHASE 6: NOTIFICATION                                         │
    │  • Send email: "Daily Status Report"                           │
    │    - To: Configured email addresses                            │
    │    - Attachment: Daily Excel file                              │
    │  • Send completion email with log file                         │
    └────────────────────────┬───────────────────────────────────────┘
                             │
                             ▼
    ┌────────────────────────────────────────────────────────────────┐
    │  END: Bot Execution Complete                                   │
    │  ✓ Daily report generated                                      │
    │  ✓ Master file updated                                         │
    │  ✓ Stakeholders notified                                       │
    └────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════

ERROR HANDLING FLOW:

    ┌─────────────────────────────────────────────────────────────┐
    │  TRY Block (Entire Bot Execution)                           │
    └────────────────────────┬────────────────────────────────────┘
                             │
                             │ [Error Occurs]
                             ▼
    ┌─────────────────────────────────────────────────────────────┐
    │  CATCH Block                                                │
    │  • Log error message and line number                        │
    │  • Send failure email to stakeholders                       │
    │    - Subject: "Daily Report Bot Failed"                     │
    │    - Body: Error details                                    │
    └────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
    ┌─────────────────────────────────────────────────────────────┐
    │  FINALLY Block (Always Executes)                           │
    │  • Send completion email with log file                      │
    │  • Log: "Report Bot Execution completed"                    │
    └─────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════

RETRY LOGIC (SharePoint Operations):

    ┌─────────────────────────────────────────────────────────────┐
    │  Initialize: RetryCount = 0, MaxRetry = 10                 │
    └────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
    ┌─────────────────────────────────────────────────────────────┐
    │  WHILE (RetryCount < MaxRetry) AND (Success = False)       │
    │  ┌───────────────────────────────────────────────────────┐ │
    │  │  TRY:                                                 │ │
    │  │    • Kill Excel processes                             │ │
    │  │    • Copy file                                        │ │
    │  │    • Set Success = True                               │ │
    │  │    • Log success                                      │ │
    │  └───────────────────────────────────────────────────────┘ │
    │                           │                                 │
    │                           │ [Error]                         │
    │                           ▼                                 │
    │  ┌───────────────────────────────────────────────────────┐ │
    │  │  CATCH:                                               │ │
    │  │    • Increment RetryCount                             │ │
    │  │    • Log retry attempt number                         │ │
    │  │    • Wait 5 seconds                                   │ │
    │  │    • Continue loop                                    │ │
    │  └───────────────────────────────────────────────────────┘ │
    └─────────────────────────┬───────────────────────────────────┘
                             │
                             ▼
    ┌─────────────────────────────────────────────────────────────┐
    │  IF Success = True: Continue                                │
    │  IF RetryCount = MaxRetry: Throw Error                      │
    └─────────────────────────────────────────────────────────────┘
```

---

## 2. Component Breakdown

### Main Components

| Component | Type | Purpose |
|-----------|------|---------|
| **Report_Main** | Task Bot | Main orchestrator - handles email, file management, SharePoint sync |
| **SubTask_Report** | Task Bot | Reusable component - processes individual bot report files and calculates metrics |
| **Bot_Config.xlsx** | Config File | Contains bot names, folder paths, status columns, logic types, keywords |
| **General_Config** | Config Sheet | Stores SharePoint path, email addresses, main file path |

### Key Packages Used
- **Excel_MS (v6.23.x)** - Excel file operations (open, read, write, close)
- **Email (v3.33.1)** - Outlook integration for reading/sending emails
- **File/Folder (v6.13.0)** - File system operations (copy, delete, move)
- **LogToFile (v3.10.0)** - Audit trail logging with timestamps
- **DataTable (v4.17.0)** - In-memory data manipulation
- **ErrorHandler (v2.13.0)** - Try-catch blocks with retry logic
- **String/Number** - Data type conversions and manipulations
- **Datetime (v2.16.1)** - Date calculations and formatting

---

## 3. Detailed Process Flow

### Step-by-Step Flow with Key Logic

#### **Phase 1: Initialization**
1. Kill all Excel processes (`Taskkill /t /IM EXCEL.EXE /f`)
2. Calculate dates:
   - `bottime` = Current timestamp (format: ddMMyy_HH_mm) for log file naming
   - `yesterday` = Today - 1 day (report date)
   - `Report_date` = Yesterday formatted as "dd-MMM" (e.g., "14-Jun")

#### **Phase 2: Folder Setup**
3. Create folders if they don't exist:
   - `C:\RPAProcesses\Report_Bot\Audit_logs` (log files)
   - `C:\RPAProcesses\Report_Bot\Daily_Report` (daily summaries)
   - `C:\RPAProcesses\Report_Bot\Main_Report` (working copy of master)
   - `C:\RPAProcesses\Report_Bot\Archive\Main_Report` (backups)
4. Create daily Excel file: `{Report_date}.xlsx` with headers:
   - Date | Bot Name | Total Volume | Total Success | Total Exception | Total Failure | Remarks

#### **Phase 3: Configuration Loading**
5. Open `Bot_Config.xlsx` from Config folder
6. Read **Sheet1** (Bot Configuration):
   - BotName, FolderPath, ArchivePath, StatusColumn, LogicType, CheckColumn, Keyword, FileKeyword
7. For each bot config row:
   - Create Input folder if missing
   - Create Archive folder if missing
   - Move old files from Input to Archive (cleanup)
8. Read **General_Config** sheet:
   - SharepointFolderLink (master file location)
   - Email Addresses (recipients)
   - Main File Path (local master file)

#### **Phase 4: Email Processing**
9. Connect to Outlook (20-second delay for sync)
10. Loop through emails in "Report" folder:
    - Date range: Yesterday to Today
    - For each email, loop through bot configs:
      - If email subject contains `Keyword`, save attachment to `FolderPath`
11. **Special Case - Cash App Remittance:**
    - If subject contains "Error-Cash App Remittance":
      - Extract error message from email body (between "Error Message:" and "Error Line No:")
      - Increment `MailFailure` counter
      - Store remarks in `AllMailRemarks`

#### **Phase 5: Data Processing (SubTask_Report)**
12. For each bot in config:
    - Pass parameters: BotName, FolderPath, StatusColumn, LogicType, CheckColumn, FileKeyword, etc.
    - SubTask processes files and returns: Volume, Success, Exception, Failure counts
    - **Logic Types Supported:**
      - **Status** - Checks status column for "success", "exception", or failure
      - **KeywordCheck** - Looks for "parked" status (treated as exception)
      - **CMT** - Checks if status column is not empty (success) or empty (exception)
      - **HeaderPR** - Checks Loop="H" and Remark="Success"
      - **RTLStatus** - Checks if Status/Exception column contains "released"
      - **CreditRisk** - Checks if status contains specific file path
13. Update daily Excel file with calculated metrics

#### **Phase 6: SharePoint Synchronization**
14. **Copy FROM SharePoint** (with retry logic, max 10 attempts):
    - Copy master file from SharePoint to `Main_Folder`
    - 5-second delay between retries if failed
15. Open both files:
    - Daily file (today's summary)
    - Main file (master historical data)
16. Get row count in Main file, calculate `NewRow = RowsCount + 1`
17. Loop through daily data and append to Main file:
    - Copy: Date, Bot Name, Volume, Success, Exception, Failure, Remarks
18. Close both files with save
19. **Copy TO SharePoint** (with retry logic, max 10 attempts):
    - Copy updated Main file back to SharePoint
    - Create archive copy: `{bottime}.xlsx` in Archive folder
    - 5-second delay between retries if failed

#### **Phase 7: Notification**
20. Send email with subject "Daily Status Report":
    - Attachment: Daily Excel file
    - Recipients: From `Toemail` config
21. Send completion email with log file attached

### Major Decision Points

| Decision Point | Condition | Action |
|----------------|-----------|--------|
| **File Extension Check** | If NOT (.xlsx, .csv, .xls) | Skip file, log warning |
| **File Keyword Filter** | If FileKeyword specified AND filename doesn't contain it | Skip file |
| **CheckColumn Logic** | If CheckColumn is empty | Use standard logic types |
| **CheckColumn Logic** | If CheckColumn has value AND row value is not empty | Process row with logic type |
| **Cash App Special Case** | If BotName = "Cash App Remittance" AND MailFailure > 0 | Add mail failures to total |
| **SharePoint Copy Retry** | If copy fails | Retry up to 10 times with 5-sec delay |

---

## 4. Applications & Integrations

### Applications Used

| Application | Purpose | Interaction Method |
|-------------|---------|-------------------|
| **Microsoft Outlook** | Email source for reports | Email package - Connect, Read, Save Attachments |
| **Microsoft Excel** | Report file format | Excel_MS package - Open, Read, Write, Close |
| **SharePoint** | Master file storage | File copy operations via UNC path |
| **File System** | Local file management | File/Folder packages - Copy, Delete, Create |

### Integration Details

#### **Outlook Integration**
- **Connection Type:** Desktop Outlook (not EWS/IMAP)
- **Folder:** "Report" folder
- **Date Filter:** Yesterday to Today (local timezone)
- **Read Status:** ALL (reads both read and unread)
- **Message Format:** PLAINTEXT
- **Delay:** 20-second wait after connection for email sync

#### **Excel Integration**
- **File Access Mode:** EDIT (read/write)
- **Header Handling:** Configurable per file
- **Read Option:** READ_CELL_TEXT (preserves formatting)
- **Session Management:** Named sessions (BotConfigSession, ExcelSession, Daily, Main, DailyFile)
- **Auto-close:** Always closes with save

#### **SharePoint Integration**
- **Method:** File copy via UNC path (e.g., `\\sharepoint\site\folder\file.xlsx`)
- **Authentication:** Windows integrated (bot runner account)
- **Retry Logic:** 10 attempts with 5-second delays
- **Backup:** Creates timestamped archive copy

---

## 5. Key Variables & Assets

### Important Variables

#### **Input Variables (SubTask_Report)**
| Variable | Type | Purpose |
|----------|------|---------|
| `BotName` | String | Name of bot being processed |
| `FolderPath` | String | Location of input Excel files |
| `StatusColumn` | String | Column name containing status |
| `LogicType` | String | Processing logic (Status, KeywordCheck, CMT, etc.) |
| `CheckColumn` | String | Optional column for row filtering |
| `FileKeyword` | String | Optional filename filter |
| `LogFilePath` | String | Path to audit log file |
| `DailyFilepath` | String | Path to daily summary file |
| `Report_date` | String | Report date (dd-MMM format) |

#### **Output Variables (SubTask_Report)**
| Variable | Type | Purpose |
|----------|------|---------|
| `Volume` | Number | Total transactions processed |
| `Success` | Number | Successful transactions |
| `Exception` | Number | Business exceptions |
| `Failure` | Number | Technical failures |
| `Remark` | String | Additional notes/error messages |

#### **Global Variables (Report_Main)**
| Variable | Type | Purpose |
|----------|------|---------|
| `RetryCount` | Number | Current retry attempt (0-10) |
| `MaxRetry` | Number | Maximum retries (10) |
| `CopySuccess` | Boolean | SharePoint copy status flag |
| `PasteSuccess` | Boolean | SharePoint paste status flag |
| `MailFailure` | Number | Email-reported failures (Cash App) |
| `AllMailRemarks` | String | Concatenated error messages from emails |

### Credential Vault Usage
**None** - Bot uses Windows integrated authentication for:
- Outlook (current user's mailbox)
- SharePoint (UNC path access)
- File system operations

### Config Files & External Dependencies

#### **Bot_Config.xlsx Structure**

**Sheet1 (Bot Configuration):**
| Column | Description | Example |
|--------|-------------|---------|
| BotName | Display name | "Indirect PO Creation" |
| FolderPath | Input folder | `C:\RPAProcesses\Report_Bot\Input\PO_Creation` |
| ArchivePath | Archive folder | `C:\RPAProcesses\Report_Bot\Archive\PO_Creation` |
| StatusColumn | Status column name | "Status" or "Remark" |
| LogicType | Processing logic | "Status", "KeywordCheck", "CMT", "HeaderPR", "RTLStatus", "CreditRisk" |
| CheckColumn | Optional filter column | "Loop" or "" (empty) |
| Keyword | Email subject keyword | "PO Creation Report" |
| FileKeyword | Filename filter | "PO_Summary" or "" (empty) |

**General_Config Sheet:**
| Parameter | Value Example |
|-----------|---------------|
| Sharepoint Path | `\\sharepoint.company.com\sites\RPA\Reports\Master_Report.xlsx` |
| Email Addresses | `rpa.support@company.com; manager@company.com` |
| Main File Path | `C:\RPAProcesses\Report_Bot\Main_Report\Master_Report.xlsx` |

---

## 6. Error Handling & Logging

### Error Handling Mechanisms

#### **Try-Catch Blocks**
1. **Main Bot Level:**
   - Wraps entire execution
   - Catches: BotException
   - Action: Log error, send failure email, execute finally block

2. **SharePoint Copy (FROM):**
   - Retry loop with try-catch
   - Max retries: 10
   - Delay: 5 seconds between attempts
   - Logs each retry attempt

3. **SharePoint Copy (TO):**
   - Retry loop with try-catch
   - Max retries: 10
   - Delay: 5 seconds between attempts
   - Logs each retry attempt

4. **SubTask Processing:**
   - Try-catch around status column reading
   - Fallback to Exception column if Status column missing
   - Continues processing on error

#### **Retry Logic**
```
WHILE (RetryCount < MaxRetry) AND (CopySuccess = False)
  TRY
    Copy file
    Set CopySuccess = True
  CATCH
    Increment RetryCount
    Log retry attempt
    Wait 5 seconds
  END TRY
END WHILE
```

### Logging Mechanisms

#### **Log File Details**
- **Location:** `C:\RPAProcesses\Report_Bot\Audit_logs\Log_file{timestamp}.txt`
- **Format:** `[Timestamp] Message`
- **Encoding:** ANSI
- **Append Mode:** Yes (except first entry which overwrites)

#### **Key Log Entries**
| Event | Log Message |
|-------|-------------|
| Bot Start | "Report Bot Execution Started." |
| Config Loaded | "Report Bot execution started and Config file is opened" |
| Outlook Connected | "Outlook is connected" |
| File Downloaded | "Input file is downloaded and pasted to {FolderPath}" |
| SubTask Started | "Subtask execution intiated for {BotName}" |
| File Processing | "{filePath} started processing." |
| SharePoint Copy | "Copy sharepoint file to main file." |
| SharePoint Update | "Sharepoint has been updated" |
| Email Sent | "Report has sent to support team." |
| Bot Complete | "Report Bot Execution completed." |
| Error | "Report Bot Execution Failed due to {ErrorMessage} at line number {ErrorLineNumber}" |

#### **Control Room Logs**
- **Activity Logs:** Available in Control Room → Activity → Bot Activity
- **Audit Trail:** All bot runs logged with start/end time, status, user
- **Error Screenshots:** Not configured (no screenshot on error)

---

## 7. Known Failure Points (Critical for L1 Support)

### Common Breakpoints

#### **1. Outlook Connection Issues**
**Symptoms:**
- Bot fails at "Connecting to outlook" step
- Error: "Unable to connect to Outlook"

**Causes:**
- Outlook not running on bot runner machine
- Outlook profile not configured
- Outlook in safe mode
- Network connectivity issues

**L1 Checks:**
- Is Outlook open on the bot runner machine?
- Can you manually open Outlook and see emails?
- Check if "Report" folder exists in Outlook

#### **2. Email Attachment Not Found**
**Symptoms:**
- Bot completes but no files in Input folders
- Log shows: "Input file is downloaded" but folder is empty

**Causes:**
- Email subject doesn't match Keyword in config
- Email doesn't have attachments
- Email date is not yesterday
- Email is in wrong folder (not "Report" folder)

**L1 Checks:**
- Verify emails exist in "Report" folder for yesterday's date
- Check email subject contains exact keyword from config
- Confirm email has Excel attachment

#### **3. SharePoint File Access Failure**
**Symptoms:**
- Bot fails with "Issue in copying sharepoint file to main file"
- Retry count reaches 10

**Causes:**
- SharePoint path incorrect or changed
- Network drive not mapped
- File locked by another user
- Insufficient permissions
- Network connectivity issues

**L1 Checks:**
- Can you manually open the SharePoint file path in File Explorer?
- Is the file locked? (Check if someone has it open)
- Verify network connectivity to SharePoint server
- Check bot runner account has read/write permissions

#### **4. Excel File Format Issues**
**Symptoms:**
- Bot skips files with log: "Input excel file not exist at {path} with correct excel formatting"
- SubTask fails with Excel-related error

**Causes:**
- File extension not .xlsx, .csv, or .xls
- File is corrupted
- File is password-protected
- File has macros that prevent opening

**L1 Checks:**
- Verify file extension is .xlsx, .csv, or .xls
- Try opening file manually in Excel
- Check if file is password-protected
- Look for file corruption indicators

#### **5. Configuration File Issues**
**Symptoms:**
- Bot fails immediately after start
- Error: "File not found" for Bot_Config.xlsx

**Causes:**
- Config file missing from `C:\RPAProcesses\Report_Bot\Config`
- Config file renamed
- Config file corrupted
- Required columns missing in config

**L1 Checks:**
- Verify `Bot_Config.xlsx` exists in Config folder
- Open config file and check Sheet1 and General_Config sheets exist
- Verify all required columns are present

#### **6. Folder Permission Issues**
**Symptoms:**
- Bot fails with "Access denied" errors
- Cannot create folders or files

**Causes:**
- Bot runner account lacks permissions
- Folder path doesn't exist
- Drive is full
- Antivirus blocking file operations

**L1 Checks:**
- Verify bot runner account has read/write permissions to all folders
- Check disk space on C: drive
- Temporarily disable antivirus and test

### Dependency Failures

#### **File Path Dependencies**
| Path | Purpose | Failure Impact |
|------|---------|----------------|
| `C:\RPAProcesses\Report_Bot\Config\Bot_Config.xlsx` | Configuration | Bot cannot start |
| `C:\RPAProcesses\Report_Bot\Audit_logs\` | Logging | Bot fails (cannot write logs) |
| `C:\RPAProcesses\Report_Bot\Daily_Report\` | Daily files | Bot fails (cannot create daily file) |
| `C:\RPAProcesses\Report_Bot\Main_Report\` | Working copy | Bot fails (cannot process data) |
| SharePoint UNC path | Master file | Bot fails (cannot sync data) |
| Input folders (per bot) | Report files | Specific bot skipped, others continue |

#### **Credential Dependencies**
- **Windows Account:** Bot runner must have:
  - Outlook access (mailbox permissions)
  - SharePoint access (site permissions)
  - Local folder access (read/write)
- **No Credential Vault:** All authentication is Windows integrated

#### **Network Dependencies**
- **Outlook Server:** Must be reachable for email operations
- **SharePoint Server:** Must be reachable for file sync
- **Network Drives:** If SharePoint uses mapped drives, must be connected

### Data-Related Issues

#### **1. Missing Status Column**
**Symptom:** SubTask fails with column not found error

**Cause:** StatusColumn name in config doesn't match actual column in Excel

**L1 Fix:** Verify column name in config matches Excel file exactly (case-sensitive)

#### **2. Unexpected Status Values**
**Symptom:** All transactions counted as Failure

**Cause:** Status values don't match expected keywords ("success", "exception", "parked", "released")

**L1 Check:** Open input file and verify status values match logic type expectations

#### **3. Empty Input Files**
**Symptom:** Bot completes but all counts are zero

**Cause:** Excel file has headers but no data rows

**L1 Check:** Open input file and verify data rows exist below header

---

## 8. Checklist for L1 Troubleshooting

### Pre-Execution Checks
- [ ] Bot runner machine is online and accessible
- [ ] Outlook is running on bot runner machine
- [ ] Bot runner account is logged in (not locked)
- [ ] Sufficient disk space on C: drive (>1GB free)
- [ ] Network connectivity to SharePoint server

### Bot Run Status Checks
- [ ] Check Control Room for bot run status (Success/Failed/In Progress)
- [ ] Review bot activity log in Control Room
- [ ] Check last successful run date/time
- [ ] Verify bot is not already running (avoid duplicate runs)

### Input File Validation
- [ ] Emails exist in Outlook "Report" folder for yesterday's date
- [ ] Email subjects contain keywords from config
- [ ] Emails have Excel attachments
- [ ] Attachment file extensions are .xlsx, .csv, or .xls
- [ ] Files can be opened manually in Excel (not corrupted)
- [ ] Files contain data rows (not just headers)

### Credential Validation
- [ ] Bot runner account password not expired
- [ ] Account has Outlook mailbox access
- [ ] Account has SharePoint site permissions
- [ ] Account has read/write access to all local folders

### Configuration Validation
- [ ] `Bot_Config.xlsx` exists in Config folder
- [ ] Config file can be opened in Excel
- [ ] Sheet1 and General_Config sheets exist
- [ ] All required columns present in config
- [ ] SharePoint path in General_Config is correct
- [ ] Email addresses in General_Config are valid

### Application Availability
- [ ] Outlook is running and responsive
- [ ] SharePoint site is accessible (test in browser)
- [ ] Excel application is installed and licensed
- [ ] No Excel processes hung in Task Manager

### Log File Review
- [ ] Latest log file exists in Audit_logs folder
- [ ] Log file shows "Report Bot Execution Started"
- [ ] Log file shows "Outlook is connected"
- [ ] Log file shows "Config file is opened"
- [ ] Check for error messages in log file
- [ ] Note the last successful step before failure

### Output Validation
- [ ] Daily Excel file created in Daily_Report folder
- [ ] Daily file contains data rows
- [ ] Master file updated in SharePoint
- [ ] Email sent to stakeholders (check Sent Items)
- [ ] Email has daily file attachment

---

## 9. When to Escalate to L2

### Escalation Scenarios

#### **Immediate L2 Escalation (Critical)**
1. **Bot Logic Failures:**
   - Incorrect calculations (Volume, Success, Exception, Failure counts)
   - Wrong data being written to reports
   - Data corruption in master file

2. **Code Changes Required:**
   - New bot needs to be added to reporting
   - New logic type needed for status processing
   - Config file structure needs modification
   - Email folder or subject line patterns changed

3. **Application/API Structural Changes:**
   - Outlook folder structure changed
   - SharePoint site migrated to new location
   - Excel file format changed (new columns, different structure)
   - Email format changed (attachment naming, subject patterns)

#### **L2 Escalation After L1 Troubleshooting**
4. **Persistent Technical Issues:**
   - SharePoint copy fails after verifying permissions and connectivity
   - Outlook connection fails despite Outlook working manually
   - Excel files fail to open despite being valid format
   - Retry logic exhausted (10 attempts) with no clear cause

5. **Configuration Issues:**
   - Config file structure appears correct but bot still fails
   - Logic type not working as expected
   - Need to add new logic type for different status patterns

6. **Performance Issues:**
   - Bot taking significantly longer than usual (>2 hours)
   - Memory issues or resource exhaustion
   - Bot hanging at specific step repeatedly

#### **L2 Escalation with Information**
When escalating, provide:
- [ ] Bot run ID from Control Room
- [ ] Complete log file from Audit_logs folder
- [ ] Screenshot of error from Control Room
- [ ] List of L1 checks performed
- [ ] Sample input files (if data-related issue)
- [ ] Config file (if configuration-related)
- [ ] Exact error message and line number
- [ ] Time of failure and duration

### L1 vs L2 Responsibility Matrix

| Issue Type | L1 Action | L2 Action |
|------------|-----------|-----------|
| Outlook not running | Restart Outlook | Investigate Outlook profile issues |
| File not found | Verify file exists, check path | Modify code to handle missing files |
| SharePoint access denied | Check permissions | Reconfigure authentication method |
| Wrong status count | Verify input data | Debug calculation logic |
| New bot to add | Request L2 support | Update config, test, deploy |
| Email not received | Verify email sent | Modify email filter logic |
| Excel file corrupted | Request new file | Add file validation logic |
| Config file missing | Restore from backup | Recreate config structure |

---

## 10. Improvement Opportunities (L2 Perspective)

### Stability Improvements

#### **1. Enhanced Error Handling**
**Current State:** Basic try-catch with retry logic

**Recommendations:**
- Add specific error handling for common Excel errors (file locked, corrupted)
- Implement exponential backoff for SharePoint retries (5s, 10s, 20s, 40s)
- Add email notification for specific error types (not just generic failure)
- Capture screenshots on error for better debugging

#### **2. Input Validation**
**Current State:** Minimal validation (file extension check only)

**Recommendations:**
- Validate Excel file structure before processing (check required columns exist)
- Validate config file on bot start (check all required fields populated)
- Add data type validation (ensure status columns contain expected values)
- Implement file size checks (warn if file unusually large/small)

#### **3. Dependency Checks**
**Current State:** No pre-flight checks

**Recommendations:**
- Add Outlook connectivity test before processing emails
- Verify SharePoint path accessible before starting
- Check disk space before creating files
- Validate all folder paths exist before processing

### Performance Improvements

#### **1. Parallel Processing**
**Current State:** Sequential processing of each bot

**Recommendations:**
- Process multiple bot reports in parallel (if machine resources allow)
- Use parallel file copy for SharePoint operations
- Batch Excel operations where possible

#### **2. Optimize Excel Operations**
**Current State:** Opens/closes Excel multiple times

**Recommendations:**
- Keep Excel sessions open longer to reduce overhead
- Use bulk write operations instead of cell-by-cell
- Consider CSV format for faster processing (if formatting not needed)

#### **3. Reduce Wait Times**
**Current State:** Fixed 20-second wait for Outlook sync

**Recommendations:**
- Implement dynamic wait (check if emails loaded, max 60 seconds)
- Remove unnecessary delays
- Use asynchronous operations where possible

### Maintainability Improvements

#### **1. Configuration Management**
**Current State:** Excel-based config file

**Recommendations:**
- Move to JSON/YAML config for better version control
- Implement config validation on load
- Add config file versioning
- Create config backup before each run

#### **2. Code Modularity**
**Current State:** Large monolithic main bot

**Recommendations:**
- Extract SharePoint operations to separate reusable bot
- Create dedicated email processing bot
- Separate Excel operations into utility bot
- Implement proper error handling bot

#### **3. Logging Enhancements**
**Current State:** Basic text file logging

**Recommendations:**
- Add log levels (INFO, WARN, ERROR, DEBUG)
- Include execution metrics (duration, memory usage)
- Log input/output data samples for debugging
- Implement structured logging (JSON format)
- Add correlation IDs for tracking across components

### Reusability Improvements

#### **1. Generic Report Processor**
**Current State:** Hardcoded for specific report structure

**Recommendations:**
- Make SubTask_Report fully configurable (column mappings in config)
- Support multiple status column patterns
- Allow custom calculation formulas
- Enable plugin architecture for new logic types

#### **2. Shared Components**
**Current State:** Code duplication between bots

**Recommendations:**
- Create reusable Excel utility bot (open, read, write, close)
- Build SharePoint connector bot (copy, paste, archive)
- Develop email utility bot (connect, read, save attachments)
- Implement common error handler bot

### Monitoring Enhancements

#### **1. Real-Time Monitoring**
**Current State:** Post-execution email only

**Recommendations:**
- Send progress notifications (25%, 50%, 75%, 100%)
- Implement heartbeat mechanism (bot alive check)
- Add Control Room dashboard integration
- Create real-time alert system for critical errors

#### **2. Metrics & Analytics**
**Current State:** Basic success/failure counts

**Recommendations:**
- Track bot execution duration trends
- Monitor file processing times per bot
- Calculate success rate trends over time
- Alert on anomalies (sudden drop in volume, spike in failures)
- Create weekly/monthly summary reports

#### **3. Health Checks**
**Current State:** No proactive monitoring

**Recommendations:**
- Daily pre-run health check (Outlook, SharePoint, disk space)
- Automated config file validation
- Dependency availability checks
- Predictive failure detection (based on historical patterns)

### Security Improvements

#### **1. Credential Management**
**Current State:** Windows integrated authentication only

**Recommendations:**
- Implement Credential Vault for sensitive data
- Rotate service account passwords regularly
- Add audit trail for file access
- Encrypt sensitive data in config file

#### **2. Data Protection**
**Current State:** No encryption for files

**Recommendations:**
- Encrypt log files (contain sensitive data)
- Implement secure file transfer for SharePoint
- Add data masking for sensitive fields in logs
- Implement file integrity checks (checksums)

---

## Appendix A: Folder Structure

```
C:\RPAProcesses\Report_Bot\
├── Config\
│   └── Bot_Config.xlsx (Configuration file)
├── Audit_logs\
│   └── Log_file{timestamp}.txt (Execution logs)
├── Daily_Report\
│   └── {dd-MMM}.xlsx (Daily summary files)
├── Main_Report\
│   └── Master_Report.xlsx (Working copy of master)
├── Archive\
│   └── Main_Report\
│       └── {timestamp}.xlsx (Archived master files)
└── Input\ (Per bot, created dynamically)
    ├── Bot1_Input\
    ├── Bot2_Input\
    └── Archive\ (Per bot)
        ├── Bot1_Archive\
        └── Bot2_Archive\
```

---

## Appendix B: Logic Type Reference

| Logic Type | Description | Success Criteria | Exception Criteria | Use Case |
|------------|-------------|------------------|-------------------|----------|
| **Status** | Standard status check | Status = "success" | Status contains "exception" | Most common bots |
| **KeywordCheck** | Keyword-based status | Status contains "parked" | Status doesn't contain "parked" | Bots with parked items |
| **CMT** | Comment field check | StatusColumn not empty | StatusColumn empty | Bots using comment field |
| **HeaderPR** | Header row check | Loop="H" AND Remark="Success" | Loop="H" AND Remark≠"Success" | PR creation bots |
| **RTLStatus** | Release status check | Status contains "released" | Status doesn't contain "released" | RTL bots |
| **CreditRisk** | Path-based check | Status contains specific path | Status doesn't contain path | Credit risk bot |

---

## Appendix C: Quick Reference Commands

### Check Bot Status
```powershell
# Check if bot is running
Get-Process | Where-Object {$_.ProcessName -like "*Automation*"}

# Check Excel processes
Get-Process | Where-Object {$_.ProcessName -eq "EXCEL"}

# Kill Excel processes (if needed)
taskkill /t /IM EXCEL.EXE /f
```

### Verify File Access
```powershell
# Test SharePoint path
Test-Path "\\sharepoint\site\folder\file.xlsx"

# Check folder permissions
icacls "C:\RPAProcesses\Report_Bot"

# Check disk space
Get-PSDrive C | Select-Object Used,Free
```

### Review Logs
```powershell
# View latest log file
Get-Content "C:\RPAProcesses\Report_Bot\Audit_logs\Log_file*.txt" | Select-Object -Last 50

# Search for errors in logs
Select-String -Path "C:\RPAProcesses\Report_Bot\Audit_logs\*.txt" -Pattern "error|failed|exception"
```

---

## Document Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | June 2026 | RPA Support Team | Initial documentation based on code analysis |

---

**For L2 Support or Code Changes:**  
Contact: RPA Development Team  
Email: rpa.dev@company.com  
Escalation: Create ticket in ServiceNow with category "RPA - Code Change"