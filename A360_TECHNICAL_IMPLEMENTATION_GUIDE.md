# A360 Technical Implementation Guide
## Carhartt Reporting Bot - Developer Reference

---

## 📋 TABLE OF CONTENTS

1. [Package Dependencies](#package-dependencies)
2. [Variable Declarations](#variable-declarations)
3. [Core Implementation Patterns](#core-implementation-patterns)
4. [Excel Operations](#excel-operations)
5. [Email Operations](#email-operations)
6. [File Operations](#file-operations)
7. [Error Handling Patterns](#error-handling-patterns)
8. [Logic Type Implementation](#logic-type-implementation)
9. [Performance Optimization](#performance-optimization)
10. [Best Practices](#best-practices)
11. [Code Snippets](#code-snippets)
12. [Troubleshooting Tips](#troubleshooting-tips)

---

## 1. Package Dependencies

### Required A360 Packages

```yaml
Packages:
  - Application: 3.11.2
  - Boolean: 2.13.2
  - Comment: 2.17.0
  - DataTable: 4.17.0
  - Datetime: 2.16.1
  - Delay: 3.9.1
  - Email: 3.33.1
  - ErrorHandler: 2.13.0-20241115-120032
  - Excel_MS: 6.23.14
  - File: 6.13.0
  - Folder: 6.13.0
  - If: 3.7.14-20231116-000453
  - LogToFile: 3.10.0
  - Loop: 3.10.0-20251030-061555
  - MessageBox: 3.7.0
  - Number: 3.11.3
  - Step: 2.7.0
  - String: 5.11.3
  - System: 3.17.0
  - TaskBot: 2.10.0-20241119-100739
  - Wait: 4.11.0
  - Window: 5.11.0
```

### Package Installation Commands

```bash
# Install via Control Room Package Manager
# Navigate to: Automation > Packages > Public Workspace

# Or use AA360 CLI (if available)
aacli package install Excel_MS --version 6.23.14
aacli package install Email --version 3.33.1
aacli package install DataTable --version 4.17.0
```

---

## 2. Variable Declarations

### Main Bot Variables (Report_Main)

```javascript
// String Variables
String: bottime              // Timestamp for log file naming (ddMMyy_HH_mm)
String: AuditFolder          // Path to audit logs folder
String: LogFilePath          // Full path to current log file
String: dailyReportFolder    // Path to daily reports folder
String: DailyFilepath        // Full path to daily Excel file
String: ConfigFolder         // Path to configuration folder
String: Main_Folder          // Path to main report folder
String: Main_Archive         // Path to archive folder
String: SharepointFolderLink // UNC path to SharePoint master file
String: MainFile             // Path to local master file
String: Toemail              // Semicolon-separated email addresses
String: Report_date          // Report date in dd-MMM format
String: Todaystr             // Today's date in yyyy-MM-dd format
String: AllMailRemarks       // Accumulated error remarks from emails
String: MailRemarks          // Single error remark from email
String: ErrorMessage         // Error message from exception
String: InputFolder          // Current bot's input folder
String: ArchiveFolder        // Current bot's archive folder
String: SourcePath           // Source file path for copy operation
String: TargetPath           // Target file path for copy operation
String: BotName              // Current bot name being processed
String: FolderPath           // Current bot's folder path
String: StatusColumn         // Column name containing status
String: LogicType            // Logic type for processing
String: CheckColumn          // Optional column for filtering
String: Keyword              // Email subject keyword
String: FileKeyword          // File name keyword

// Number Variables
Number: RetryCount           // Current retry attempt (0-10)
Number: MaxRetry             // Maximum retry attempts (10)
Number: MailFailure          // Count of failures from emails
Number: RowsCount            // Row count in Excel file
Number: NewRow               // Next row number for writing
Number: ErrorLineNumber      // Line number where error occurred

// DateTime Variables
DateTime: TodayDate          // Current system date
DateTime: yesterday          // Yesterday's date (for filtering)
DateTime: Endtime            // End of date range (today)

// Boolean Variables
Boolean: CopySuccess         // Flag for successful SharePoint copy
Boolean: PasteSuccess        // Flag for successful SharePoint paste

// DataTable Variables
DataTable: BotConfigDT       // Bot configuration data
DataTable: TGeneralConfig    // General configuration data
DataTable: TodayDT           // Daily report data

// Record Variables
Record: CurrentRow           // Current row in loop iteration
Record: TableRow             // Current row in config loop
Record: OldFiles             // File properties in cleanup loop

// Dictionary Variables
Dictionary: Email            // Email properties (subject, body, etc.)
```

### SubTask Variables (SubTask_Report)

```javascript
// Input Variables (passed from main bot)
String: BotName              // Bot name (input)
String: FolderPath           // Input folder path (input)
String: StatusColumn         // Status column name (input)
String: LogicType            // Logic type (input)
String: CheckColumn          // Check column name (input)
String: FileKeyword          // File keyword (input)
String: LogFilePath          // Log file path (input)
String: DailyFilepath        // Daily file path (input)
String: Report_date          // Report date (input)
Number: MailFailure          // Mail failure count (input)
String: MailRemarks          // Mail remarks (input)
String: AllMailRemarks       // All mail remarks (input)

// Local Variables
Number: Volume               // Total transaction count
Number: Success              // Success count
Number: Exception            // Exception count
Number: Failure              // Failure count
String: Remark               // Remarks for bot
String: Status               // Current row status
String: StatusTemp           // Temporary status holder
String: filePath             // Current file path
String: RowCheckValue        // Value from check column
Number: ExcelRowsCount       // Row count in daily file
Number: NewRow               // Next row for writing
Boolean: MailAdded           // Flag for mail failure added

// DataTable Variables
DataTable: dtSummary         // Excel data from input file

// Dictionary Variables
Dictionary: TodayFiles       // File properties in loop
Dictionary: currentRow       // Current row in data loop
```

---

## 3. Core Implementation Patterns

### Pattern 1: Kill Excel Processes

**Purpose:** Prevent file locking issues

```yaml
Action: runApp
Package: Application
Parameters:
  filePath: "file://Taskkill"
  parameters: "/t /IM EXCEL.EXE /f"
  
# Alternative using PowerShell
Action: execute_command
Command: "taskkill /F /IM EXCEL.EXE"
```

**When to Use:**
- Before opening Excel files
- Before copying files to/from SharePoint
- After Excel operations complete

---

### Pattern 2: Date Calculations

**Get Yesterday's Date:**

```yaml
# Step 1: Get current date
Action: assign
Package: Datetime
Parameters:
  option: "variable"
  dateTime: $System:Date$
Output: TodayDate

# Step 2: Convert to string
Action: toString
Package: Datetime
Parameters:
  source: $TodayDate$
  selectPattern: "CUSTOM"
  patternInput: "yyyy-MM-dd"
Output: Todaystr

# Step 3: Parse back to DateTime
Action: assign
Package: Datetime
Parameters:
  option: "constant"
  source: $Todaystr$
  formatType: "custom"
  customFormat: "yyyy-MM-dd"
Output: Endtime

# Step 4: Subtract 1 day
Action: subtract
Package: Datetime
Parameters:
  source: $Endtime$
  val: 1
  unit: "DAYS"
Output: yesterday

# Step 5: Format for report
Action: toString
Package: Datetime
Parameters:
  source: $yesterday$
  selectPattern: "CUSTOM"
  patternInput: "dd-MMM"
Output: Report_date
```

---

### Pattern 3: Folder Creation with Existence Check

```yaml
Action: if
Package: If
Condition:
  conditionalName: "folderDoesNotExists"
  packageName: "Folder"
  attributes:
    folderPath: $AuditFolder$
    waitTimeout: 0
Then:
  - Action: createFolder
    Package: Folder
    Parameters:
      folderPath: $AuditFolder$
      isOverwrite: false
```

---

### Pattern 4: Retry Logic Pattern

```yaml
# Initialize retry variables
Action: assignToNumber
Package: Number
Parameters:
  input: 0
Output: RetryCount

Action: assignToNumber
Package: Number
Parameters:
  input: 10
Output: MaxRetry

Action: assign
Package: Boolean
Parameters:
  source: "constant"
  userDefined: "false"
Output: CopySuccess

# Retry loop
Action: loop
Package: Loop
LoopType: WHILE
Condition:
  operator: AND
  conditions:
    - RetryCount < MaxRetry
    - CopySuccess = False
Body:
  - Action: try
    Package: ErrorHandler
    Try:
      - # Perform operation
      - Action: copyFiles
        Package: File
        Parameters:
          sourceFilePath: $SourcePath$
          destinationPath: $TargetPath$
          isOverwrite: true
      - Action: assign
        Package: Boolean
        Parameters:
          source: "constant"
          userDefined: "true"
        Output: CopySuccess
      - Action: logToFile
        Parameters:
          logContent: "Operation successful"
    Catch:
      - Action: assignToNumber
        Package: Number
        Parameters:
          input: $RetryCount$ + 1
        Output: RetryCount
      - Action: logToFile
        Parameters:
          logContent: "Retry attempt: $RetryCount$"
      - Action: delay
        Package: Delay
        Parameters:
          delayType: "REGULAR"
          delayTime: 5
          timeUnit: "SECONDS"
```

---

## 4. Excel Operations

### Pattern 1: Open Excel File

```yaml
Action: OpenSpreadsheet
Package: Excel_MS
Parameters:
  excelSourceOption: "desktopfilepath"
  filePath: "file://$ConfigFolder$/Bot_Config.xlsx"
  containsHeader: true
  isSpecificSheet: false
  fileAccessMode: "EDIT"
  isSecure: false
  loadAddIns: false
  excludeHiddenSheets: false
  containsChart: false
  setSensitivity: false
  disableUpdateLinks: false
Output:
  sessionName: "BotConfigSession"
  sessionTarget: "LOCAL"
```

**Key Parameters:**
- `fileAccessMode: "EDIT"` - Allows read/write
- `containsHeader: true` - First row is header
- `isSpecificSheet: false` - Use active sheet
- `disableUpdateLinks: false` - Don't update external links

---

### Pattern 2: Read Excel to DataTable

```yaml
Action: getWorksheetAsDataTable
Package: Excel_MS
Parameters:
  sheetSelection: "ActiveWorksheet"  # or "SpecificSheet"
  fromSpecificSheet: "Sheet1"        # if SpecificSheet
  containsHeader: true
  readOption: "READ_CELL_TEXT"       # Read as text, not formulas
  session: "BotConfigSession"
Output: BotConfigDT
```

**Read Options:**
- `READ_CELL_TEXT` - Read displayed text (recommended)
- `READ_CELL_VALUE` - Read underlying values
- `READ_CELL_FORMULA` - Read formulas

---

### Pattern 3: Write to Specific Cell

```yaml
Action: SetCell
Package: Excel_MS
Parameters:
  cellOption: "SPECIFIC_CELL"
  cell: "A$NewRow.Number:toString$"  # Dynamic cell reference
  value: $Report_date$
  session: "DailyFile"
```

**Dynamic Cell Reference:**
```yaml
# For column A, row 5
cell: "A5"

# For dynamic row number
cell: "A$RowNumber.Number:toString$"

# For dynamic column and row
cell: "$ColumnLetter$$RowNumber.Number:toString$"
```

---

### Pattern 4: Get Row Count

```yaml
Action: getNumberOfRows
Package: Excel_MS
Parameters:
  sheetOption: "BYINDEX"
  sheetIndex: 1
  fetchRowsType: "NONEMPTY"  # or "TOTALROWS"
  session: "Main"
Output: RowsCount
```

**Fetch Types:**
- `NONEMPTY` - Count rows with data
- `TOTALROWS` - Count all rows including empty

---

### Pattern 5: Close Excel File

```yaml
Action: CloseSpreadsheet
Package: Excel_MS
Parameters:
  session: "BotConfigSession"
  isSave: true
  isDisplayErrorEnabled: false
```

**Best Practice:** Always close Excel sessions to free resources

---

### Pattern 6: Create New Excel File

```yaml
Action: CreateSpreadsheet
Package: Excel_MS
Parameters:
  filePath: "file://$DailyFilepath$"
  isOverwrite: true
  sheetName: ""  # Use default sheet name
  setSensitivity: false
Output:
  sessionName: "DailyFile"
  sessionTarget: "LOCAL"
```

---

## 5. Email Operations

### Pattern 1: Connect to Outlook

```yaml
Action: emailConnect
Package: Email
Parameters:
  session: "EmailSession"
  serverType: "OUTLOOK"
  select: "LIST"  # Use default Outlook profile
```

**Server Types:**
- `OUTLOOK` - Desktop Outlook (recommended)
- `EWS` - Exchange Web Services
- `IMAP` - IMAP server
- `SMTP` - SMTP server (send only)

---

### Pattern 2: Read Emails with Date Filter

```yaml
Action: loop
Package: Loop
LoopType: ITERATOR
Iterator:
  iteratorName: "loop.iterators.email"
  packageName: "Email"
  attributes:
    sessionName: "EmailSession"
    readStatus: "ALL"  # ALL, READ, UNREAD
    enableStatusNoUpdate: false
    sortBy: "LATEST_FIRST"
    folder: "Report"
    subject: ""  # Empty = all subjects
    from: ""     # Empty = all senders
    since: $yesterday$
    before: $Endtime$
    messageFormat: "PLAINTEXT"  # or "HTML"
    isToUseLocalTimezone: true
  returnTo: Email
Body:
  - # Process each email
```

**Key Parameters:**
- `since` / `before` - Date range filter
- `folder` - Outlook folder name
- `readStatus` - Filter by read status
- `messageFormat` - PLAINTEXT or HTML

---

### Pattern 3: Save Email Attachments

```yaml
Action: saveAttachment
Package: Email
Parameters:
  folderPath: $FolderPath$
  checkOverrwrite: false
```

**Note:** Must be inside email loop iterator

---

### Pattern 4: Send Email

```yaml
Action: SendMailV2
Package: Email
Parameters:
  toAddress: $Toemail$
  cc: ""
  bcc: ""
  replyTO: ""
  invalidAddress: false
  importance: "Normal"  # Normal, High, Low
  subject: "Daily Status Report"
  fileList:
    - "file://$DailyFilepath$"
  ensureAttachmentsExist: false
  bodyFormat: "PLAINTEXT"  # or "HTML"
  message: "Hi All,\n\nPlease find the Daily status report attached.\n\nRegards,\nReport Bot."
  goGreen: true  # Don't include original message
  serverType: "OUTLOOK"
```

**Multiple Recipients:**
```yaml
toAddress: "user1@company.com; user2@company.com; user3@company.com"
```

**Multiple Attachments:**
```yaml
fileList:
  - "file://$DailyFilepath$"
  - "file://$LogFilePath$"
  - "file://$ArchiveFile$"
```

---

### Pattern 5: Extract Text from Email Body

```yaml
Action: beforeAfter
Package: String
Parameters:
  sourceString: $Email{emailMessage}$
  getCharacters: "BEFOREAFTER"
  beforeStringInBeforeAfter: "Error Message:"
  beforeOccurrenceInBeforeAfter: 1
  beforeAfterCondition: "AND"
  afterStringInBeforeAfter: "Error Line No:"
  afterOccurrenceInBeforeAfter: 1
  ifNoMatchFound: "EMPTY"
  noOfCharsToGet: "ALL"
  isCaseSensitive: "true"
  trimSpaces: true
  removeEnter: true
Output: MailRemarks
```

---

## 6. File Operations

### Pattern 1: Copy Files

```yaml
Action: copyFiles
Package: File
Parameters:
  sourceFilePath: "file://$SourcePath$"
  destinationPath: $TargetPath$
  isOverwrite: true
  isParallel: false
  isSize: false
  isDate: false
```

**Parameters:**
- `isOverwrite` - Overwrite if exists
- `isParallel` - Copy multiple files in parallel
- `isSize` - Filter by file size
- `isDate` - Filter by date

---

### Pattern 2: Delete Files

```yaml
Action: deleteFiles
Package: File
Parameters:
  filePath: "file://$SourcePath$"
  isParallelDelete: false
  isSize: false
  isDate: false
```

---

### Pattern 3: Loop Through Files

```yaml
Action: loop
Package: Loop
LoopType: ITERATOR
Iterator:
  iteratorName: "loop.iterators.files"
  packageName: "File"
  attributes:
    folderPath: $InputFolder$
  returnTo: TodayFiles
Body:
  - # Access file properties
  - # $TodayFiles{name}$ - File name without extension
  - # $TodayFiles{extension}$ - File extension
  - # $TodayFiles{size}$ - File size in bytes
  - # $TodayFiles{lastModified}$ - Last modified date
```

---

### Pattern 4: Check File Extension

```yaml
Action: if
Package: If
Condition:
  operator: AND
  conditions:
    - $TodayFiles{extension}$ NEQ "xlsx"
    - $TodayFiles{extension}$ NEQ "csv"
    - $TodayFiles{extension}$ NEQ "xls"
Then:
  - Action: logToFile
    Parameters:
      logContent: "Invalid file format: $TodayFiles{extension}$"
  - Action: loop.commands.continue
    Package: Loop
    Parameters:
      anchor: "main"
```

---

## 7. Error Handling Patterns

### Pattern 1: Try-Catch-Finally

```yaml
Action: try
Package: ErrorHandler
Try:
  - # Main execution steps
  - Action: copyFiles
    Parameters:
      sourceFilePath: $SourcePath$
      destinationPath: $TargetPath$
Catch:
  - Action: catch
    Package: ErrorHandler
    Parameters:
      exceptionType: "BotException"
      continueOnError: true
    Returns:
      errorMessage: ErrorMessage
      errorLineNumber: ErrorLineNumber
    Body:
      - Action: logToFile
        Parameters:
          logContent: "Error: $ErrorMessage$ at line $ErrorLineNumber$"
      - Action: SendMailV2
        Parameters:
          subject: "Bot Failed"
          message: "Error: $ErrorMessage$"
Finally:
  - Action: finally
    Package: ErrorHandler
    Body:
      - Action: logToFile
        Parameters:
          logContent: "Execution completed"
      - Action: SendMailV2
        Parameters:
          subject: "Bot Completed"
```

---

### Pattern 2: Continue on Error

```yaml
Action: try
Package: ErrorHandler
Try:
  - # Risky operation
Catch:
  - Action: catch
    Parameters:
      exceptionType: "BotException"
      continueOnError: true  # Don't stop execution
    Body:
      - Action: logToFile
        Parameters:
          logContent: "Non-critical error occurred"
```

---

### Pattern 3: Throw Custom Error

```yaml
Action: throw
Package: ErrorHandler
Parameters:
  errorMessage: "Configuration file not found"
  errorCode: "ERR-001"
```

---

## 8. Logic Type Implementation

### Logic Type 1: Status

```yaml
# Check if CheckColumn is empty OR has value
Action: if
Package: If
Condition:
  operator: OR
  conditions:
    - $CheckColumn$ EQ ""
    - $currentRow{$CheckColumn$}$ NEQ ""
Then:
  # Increment volume
  - Action: assignToNumber
    Parameters:
      input: $Volume$ + 1
    Output: Volume
  
  # Get status and convert to lowercase
  - Action: assign
    Package: String
    Parameters:
      sourceString: $currentRow{$StatusColumn$}$
    Output: Status
  
  - Action: lowercase
    Package: String
    Parameters:
      sourceString: $Status$
    Output: Status
  
  # Check status value
  - Action: if
    Condition: $Status$ INCLUDE "exception"
    Then:
      - Action: assignToNumber
        Parameters:
          input: $Exception$ + 1
        Output: Exception
    ElseIf: $Status$ EQ "success"
    Then:
      - Action: assignToNumber
        Parameters:
          input: $Success$ + 1
        Output: Success
    Else:
      - Action: assignToNumber
        Parameters:
          input: $Failure$ + 1
        Output: Failure
```

---

### Logic Type 2: KeywordCheck

```yaml
Action: if
Condition:
  operator: OR
  conditions:
    - $CheckColumn$ EQ ""
    - $currentRow{$CheckColumn$}$ NEQ ""
Then:
  - Action: assignToNumber
    Parameters:
      input: $Volume$ + 1
    Output: Volume
  
  - Action: assign
    Parameters:
      sourceString: $currentRow{$StatusColumn$}$
    Output: Status
  
  - Action: lowercase
    Parameters:
      sourceString: $Status$
    Output: Status
  
  - Action: if
    Condition: $Status$ INCLUDE "parked"
    Then:
      - Action: assignToNumber
        Parameters:
          input: $Success$ + 1
        Output: Success
    Else:
      - Action: assignToNumber
        Parameters:
          input: $Exception$ + 1
        Output: Exception
```

---

### Logic Type 3: CMT (Comment Check)

```yaml
Action: if
Condition:
  operator: OR
  conditions:
    - $CheckColumn$ EQ ""
    - $currentRow{$CheckColumn$}$ NEQ ""
Then:
  - Action: assignToNumber
    Parameters:
      input: $Volume$ + 1
    Output: Volume
  
  - Action: if
    Condition: $currentRow{$StatusColumn$}$ NEQ ""
    Then:
      - Action: assignToNumber
        Parameters:
          input: $Success$ + 1
        Output: Success
    Else:
      - Action: assignToNumber
        Parameters:
          input: $Exception$ + 1
        Output: Exception
```

---

### Logic Type 4: HeaderPR

```yaml
Action: if
Condition: $currentRow{Loop}$ EQ "H"
Then:
  - Action: assignToNumber
    Parameters:
      input: $Volume$ + 1
    Output: Volume
  
  - Action: if
    Condition: $currentRow{Remark}$ EQ "Success"
    Then:
      - Action: assignToNumber
        Parameters:
          input: $Success$ + 1
        Output: Success
    Else:
      - Action: assignToNumber
        Parameters:
          input: $Exception$ + 1
        Output: Exception
```

---

### Logic Type 5: RTLStatus

```yaml
- Action: assignToNumber
  Parameters:
    input: $Volume$ + 1
  Output: Volume

- Action: try
  Try:
    - Action: assign
      Parameters:
        sourceString: $currentRow{Status}$
      Output: StatusTemp
  Catch:
    - Action: assign
      Parameters:
        sourceString: $currentRow{Exception}$
      Output: StatusTemp

- Action: lowercase
  Parameters:
    sourceString: $StatusTemp$
  Output: StatusTemp

- Action: if
  Condition: $StatusTemp$ INCLUDE "released"
  Then:
    - Action: assignToNumber
      Parameters:
        input: $Success$ + 1
      Output: Success
  Else:
    - Action: assignToNumber
      Parameters:
        input: $Exception$ + 1
      Output: Exception
```

---

### Logic Type 6: CreditRisk

```yaml
Action: if
Condition:
  operator: OR
  conditions:
    - $CheckColumn$ EQ ""
    - $currentRow{$CheckColumn$}$ NEQ ""
Then:
  - Action: assignToNumber
    Parameters:
      input: $Volume$ + 1
    Output: Volume
  
  - Action: assign
    Parameters:
      sourceString: $currentRow{$StatusColumn$}$
    Output: Status
  
  - Action: if
    Condition: $Status$ INCLUDE "L:\Credit Risk Matrix - Data On Demand\Output"
    Then:
      - Action: assignToNumber
        Parameters:
          input: $Success$ + 1
        Output: Success
    Else:
      - Action: assignToNumber
        Parameters:
          input: $Exception$ + 1
        Output: Exception
```

---

## 9. Performance Optimization

### Tip 1: Use DataTable Instead of Row-by-Row Reading

**❌ Slow Approach:**
```yaml
# Reading cell by cell in loop
Loop through rows:
  - GetCell A$row$
  - GetCell B$row$
  - GetCell C$row$
```

**✅ Fast Approach:**
```yaml
# Read entire sheet once
Action: getWorksheetAsDataTable
Output: dtSummary

# Loop through DataTable
Loop through dtSummary:
  - Access $currentRow{ColumnName}$
```

**Performance Gain:** 10-20x faster for large files

---

### Tip 2: Minimize Excel Session Opens/Closes

**❌ Slow Approach:**
```yaml
For each file:
  - OpenSpreadsheet
  - Read data
  - CloseSpreadsheet
```

**✅ Fast Approach:**
```yaml
For each file:
  - OpenSpreadsheet
  - Read all required data
  - Perform all operations
  - CloseSpreadsheet
```

---

### Tip 3: Use Specific Sheet Selection

**❌ Slow:**
```yaml
sheetSelection: "ActiveWorksheet"
```

**✅ Fast:**
```yaml
sheetSelection: "SpecificSheet"
fromSpecificSheet: "Sheet1"
```

---

### Tip 4: Disable Unnecessary Excel Features

```yaml
Action: OpenSpreadsheet
Parameters:
  loadAddIns: false          # Don't load add-ins
  excludeHiddenSheets: false # Don't process hidden sheets
  containsChart: false       # Don't process charts
  disableUpdateLinks: false  # Don't update external links
```

---

### Tip 5: Use Parallel File Operations (When Safe)

```yaml
Action: copyFiles
Parameters:
  isParallel: true  # Copy multiple files simultaneously
```

**Caution:** Only use when files are independent

---

## 10. Best Practices

### 1. Variable Naming Conventions

```yaml
# Use descriptive names
✅ BotConfigDT
❌ dt1

# Use camelCase
✅ dailyReportFolder
❌ daily_report_folder

# Prefix by type
✅ strFileName (String)
✅ numRowCount (Number)
✅ dtSummary (DataTable)
✅ blnSuccess (Boolean)
```

---

### 2. Error Handling

```yaml
# Always wrap risky operations in try-catch
✅ Try-Catch around file operations
✅ Try-Catch around Excel operations
✅ Try-Catch around email operations

# Log all errors
✅ Log error message and line number
✅ Include context (file name, bot name)
✅ Use timestamps in logs
```

---

### 3. Logging Strategy

```yaml
# Log at key checkpoints
✅ Start of execution
✅ After each major step
✅ Before/after external system calls
✅ On errors and warnings
✅ End of execution

# Include relevant context
✅ Timestamp (automatic with appendTimestamp: true)
✅ Action performed
✅ File/folder names
✅ Counts and metrics
```

---

### 4. Session Management

```yaml
# Use descriptive session names
✅ "BotConfigSession"
✅ "DailyFile"
✅ "Main"
❌ "Session1"

# Always close sessions
✅ CloseSpreadsheet after operations
✅ Use Finally block to ensure cleanup
```

---

### 5. File Path Handling

```yaml
# Use variables for paths
✅ $ConfigFolder$/Bot_Config.xlsx
❌ C:\RPAProcesses\Report_Bot\Config\Bot_Config.xlsx

# Use file:// protocol for file paths
✅ file://$DailyFilepath$
❌ $DailyFilepath$

# Build paths dynamically
✅ $FolderPath$\$TodayFiles{name}$.$TodayFiles{extension}$
```

---

### 6. DataTable Operations

```yaml
# Access columns by name (not index)
✅ $currentRow{StatusColumn}$
✅ $currentRow{"Bot Name"}$
❌ $currentRow[2]$

# Check for empty values
✅ IF $currentRow{Status}$ NEQ ""
✅ IF $currentRow{Status}$ EQ ""
```

---

### 7. String Operations

```yaml
# Always trim user input
Action: trim
Parameters:
  sourceString: $UserInput$
  trimAtBeginning: true
  trimAtEnd: true

# Use lowercase for comparisons
Action: lowercase
Parameters:
  sourceString: $Status$
Output: Status

# Then compare
IF $Status$ EQ "success"
```

---

### 8. Loop Control

```yaml
# Use meaningful anchor names
Action: loop
Parameters:
  anchor: "main"  # or "fileLoop", "botLoop"

# Use continue for skipping
Action: loop.commands.continue
Parameters:
  anchor: "main"

# Use break for early exit
Action: loop.commands.break
Parameters:
  anchor: "main"
```

---

## 11. Code Snippets

### Snippet 1: Initialize Counters

```yaml
- Action: assignToNumber
  Package: Number
  Parameters:
    input: 0
  Output: Volume

- Action: assignToNumber
  Parameters:
    input: 0
  Output: Success

- Action: assignToNumber
  Parameters:
    input: 0
  Output: Exception

- Action: assignToNumber
  Parameters:
    input: 0
  Output: Failure
```

---

### Snippet 2: Log with Timestamp

```yaml
Action: logToFile
Package: LogToFile
Parameters:
  filePath: "file://$LogFilePath$"
  logContent: "Bot execution started for $BotName$"
  appendTimestamp: true
  logOption: "APPEND_FILE"  # or "OVERWRITE_FILE"
  encodingValue: "ANSI"     # or "UTF8"
```

---

### Snippet 3: Dynamic Cell Reference

```yaml
# Calculate next row
Action: assignToNumber
Parameters:
  input: $RowsCount$ + 1
Output: NewRow

# Write to cell
Action: SetCell
Parameters:
  cellOption: "SPECIFIC_CELL"
  cell: "A$NewRow.Number:toString$"
  value: $Report_date$
  session: "Main"
```

---

### Snippet 4: String Concatenation

```yaml
# Method 1: Direct concatenation
Action: assign
Package: String
Parameters:
  sourceString: "$FolderPath$\$FileName$"
Output: FullPath

# Method 2: Using expression
Action: assign
Parameters:
  sourceString: $AllMailRemarks$ + " " + $MailRemarks$
Output: AllMailRemarks
```

---

### Snippet 5: Conditional Assignment

```yaml
Action: if
Condition: $AllMailRemarks$ EQ ""
Then:
  - Action: assign
    Parameters:
      sourceString: $MailRemarks$
    Output: AllMailRemarks
Else:
  - Action: assign
    Parameters:
      sourceString: "$AllMailRemarks$ $MailRemarks$"
    Output: AllMailRemarks
```

---

### Snippet 6: Call SubTask Bot

```yaml
Action: runTask
Package: TaskBot
Parameters:
  taskbot:
    taskbotInput:
      type: DICTIONARY
      dictionary:
        - key: "BotName"
          value: $BotName$
        - key: "FolderPath"
          value: $FolderPath$
        - key: "StatusColumn"
          value: $StatusColumn$
        - key: "LogicType"
          value: $LogicType$
    taskbotFile:
      type: FILE
      string: "repository:///Automation%20Anywhere/Bots/Report_Bot/SubTask_Report"
  repeatOption: "DO_NOT_REPEAT"
  delayNextRepetition: false
  continueOnError: false
```

---

## 12. Troubleshooting Tips

### Issue 1: "Session not found" Error

**Cause:** Excel session closed or not created

**Solution:**
```yaml
# Always check session exists before operations
Action: if
Condition: Session "BotConfigSession" exists
Then:
  - # Perform operations
Else:
  - # Reopen session
  - Action: OpenSpreadsheet
```

---

### Issue 2: "File not found" Error

**Cause:** Incorrect file path or file doesn't exist

**Solution:**
```yaml
# Check file exists before operations
Action: if
Package: If
Condition:
  conditionalName: "fileExists"
  packageName: "File"
  attributes:
    filePath: "file://$FilePath$"
Then:
  - # Process file
Else:
  - Action: logToFile
    Parameters:
      logContent: "File not found: $FilePath$"
```

---

### Issue 3: "Column not found" Error

**Cause:** Column name doesn't match Excel header

**Solution:**
```yaml
# Use try-catch when accessing columns
Action: try
Try:
  - Action: assign
    Parameters:
      sourceString: $currentRow{$StatusColumn$}$
    Output: Status
Catch:
  - Action: logToFile
    Parameters:
      logContent: "Column not found: $StatusColumn$"
  - Action: assign
    Parameters:
      sourceString: ""
    Output: Status
```

---

### Issue 4: "Type mismatch" Error

**Cause:** Trying to use string as number or vice versa

**Solution:**
```yaml
# Convert string to number
Action: toNumber
Package: Number
Parameters:
  sourceString: $StringValue$
Output: NumberValue

# Convert number to string
Action: toString
Package: Number
Parameters:
  number: $NumberValue$
Output: StringValue
```

---

### Issue 5: Slow Excel Operations

**Cause:** Reading cell by cell instead of using DataTable

**Solution:**
```yaml
# Use getWorksheetAsDataTable
Action: getWorksheetAsDataTable
Parameters:
  sheetSelection: "SpecificSheet"
  fromSpecificSheet: "Sheet1"
  containsHeader: true
  readOption: "READ_CELL_TEXT"
  session: "ExcelSession"
Output: dtData
```

---

### Issue 6: Email Not Sending

**Cause:** Outlook not connected or session expired

**Solution:**
```yaml
# Reconnect before sending
Action: emailConnect
Parameters:
  session: "EmailSession"
  serverType: "OUTLOOK"
  select: "LIST"

# Add delay after connection
Action: delay
Parameters:
  delayType: "REGULAR"
  delayTime: 5
  timeUnit: "SECONDS"

# Then send email
Action: SendMailV2
```

---

## 13. Advanced Patterns

### Pattern 1: Dynamic Column Access

```yaml
# Store column name in variable
Action: assign
Parameters:
  sourceString: "Status"
Output: ColumnName

# Access column dynamically
Action: assign
Parameters:
  sourceString: $currentRow{$ColumnName$}$
Output: ColumnValue
```

---

### Pattern 2: Nested Loops

```yaml
Action: loop
Package: Loop
LoopType: ITERATOR
Iterator: BotConfigDT
ReturnTo: BotRow
Body:
  - Action: loop
    LoopType: ITERATOR
    Iterator: Files in folder
    ReturnTo: FileRow
    Body:
      - # Process each file for each bot
```

---

### Pattern 3: Conditional Loop Exit

```yaml
Action: loop
LoopType: WHILE
Condition: $RetryCount$ < $MaxRetry$
Body:
  - Action: if
    Condition: $Success$ EQ true
    Then:
      - Action: loop.commands.break
        Parameters:
          anchor: "retryLoop"
```

---

### Pattern 4: Multiple Conditions

```yaml
Action: if
Condition:
  operator: AND
  conditions:
    - operator: OR
      conditions:
        - $Status$ EQ "success"
        - $Status$ EQ "completed"
    - $Volume$ > 0
Then:
  - # Execute if (status is success OR completed) AND volume > 0
```

---

## 14. Testing Strategies

### Unit Testing

```yaml
# Test individual logic types
Test Case 1: Status Logic
  Input: Status = "Success"
  Expected: Success = 1, Exception = 0, Failure = 0

Test Case 2: KeywordCheck Logic
  Input: Status = "Parked"
  Expected: Success = 1, Exception = 0

Test Case 3: CMT Logic
  Input: StatusColumn = "Completed"
  Expected: Success = 1, Exception = 0
```

---

### Integration Testing

```yaml
# Test end-to-end flow
Test Scenario 1: Normal Execution
  1. Place test files in input folders
  2. Run bot
  3. Verify daily report created
  4. Verify SharePoint updated
  5. Verify email sent

Test Scenario 2: Missing Files
  1. Remove files from one bot's folder
  2. Run bot
  3. Verify bot continues
  4. Verify zero counts for missing bot
  5. Verify other bots processed
```

---

### Error Testing

```yaml
# Test error scenarios
Test Scenario 1: SharePoint Unavailable
  1. Disconnect network
  2. Run bot
  3. Verify retry logic executes
  4. Verify failure email sent

Test Scenario 2: Corrupted File
  1. Place corrupted Excel file
  2. Run bot
  3. Verify bot skips file
  4. Verify error logged
  5. Verify other files processed
```

---

## 15. Deployment Checklist

### Pre-Deployment

- [ ] All packages installed and updated
- [ ] Variables declared with correct types
- [ ] Error handling implemented
- [ ] Logging added at key points
- [ ] Configuration file validated
- [ ] Test execution successful
- [ ] Code reviewed by peer
- [ ] Documentation updated

### Deployment

- [ ] Bot uploaded to Control Room
- [ ] Dependencies checked
- [ ] Credentials configured
- [ ] Schedule created
- [ ] Permissions assigned
- [ ] Notification emails configured
- [ ] Test run in production

### Post-Deployment

- [ ] Monitor first 3 executions
- [ ] Validate output accuracy
- [ ] Check execution time
- [ ] Review logs for warnings
- [ ] Gather stakeholder feedback
- [ ] Document lessons learned

---

## 16. Quick Reference

### Common A360 Expressions

```yaml
# System variables
$System:Date$              # Current date/time
$System:UserName$          # Current user
$System:MachineName$       # Machine name

# String operations
$String1$ + $String2$      # Concatenation
$String$.Length            # String length
$String$.ToUpper()         # Uppercase
$String$.ToLower()         # Lowercase

# Number operations
$Num1$ + $Num2$            # Addition
$Num1$ - $Num2$            # Subtraction
$Num1$ * $Num2$            # Multiplication
$Num1$ / $Num2$            # Division
$Num1$ % $Num2$            # Modulo

# Conversions
$Number.Number:toString$   # Number to string
$String.String:toNumber$   # String to number

# DataTable access
$Row{ColumnName}$          # Access by column name
$Row[0]$                   # Access by index

# Dictionary access
$Dict{key}$                # Access by key
```

---

### Common File Paths

```yaml
# Configuration
C:\RPAProcesses\Report_Bot\Config\Bot_Config.xlsx

# Logs
C:\RPAProcesses\Report_Bot\Audit_logs\Log_file[timestamp].txt

# Daily Reports
C:\RPAProcesses\Report_Bot\Daily_Report\[date].xlsx

# Input Folders
C:\RPA\Input\[BotName]\

# Archive Folders
C:\RPA\Archive\[BotName]\
```

---

### Common Error Codes

```yaml
ERR-001: Config file not found
ERR-002: Outlook connection failed
ERR-003: SharePoint access denied
ERR-004: File locked
ERR-005: Invalid file format
ERR-006: Column not found
ERR-007: Disk space full
ERR-008: Network timeout
```

---

## 📚 Additional Resources

### Official Documentation
- [A360 Package Documentation](https://docs.automationanywhere.com/bundle/enterprise-v2019/page/enterprise-cloud/topics/aae-client/bot-creator/commands/cloud-commands.html)
- [A360 Best Practices](https://docs.automationanywhere.com/bundle/enterprise-v2019/page/enterprise-cloud/topics/aae-architecture-implementation/deployment-planning/best-practices.html)
- [A360 Error Handling](https://docs.automationanywhere.com/bundle/enterprise-v2019/page/enterprise-cloud/topics/aae-client/bot-creator/commands/cloud-error-handling.html)

### Community Resources
- [Automation Anywhere Community](https://community.automationanywhere.com/)
- [A360 University](https://university.automationanywhere.com/)
- [GitHub Examples](https://github.com/AutomationAnywhere)

---

**Document Version:** 1.0  
**Last Updated:** June 16, 2026  
**Author:** RPA Development Team  
**For:** Carhartt Reporting Bot Implementation

---

**💡 Pro Tip:** Bookmark this guide and refer to it during development. Copy-paste the patterns and modify as needed!