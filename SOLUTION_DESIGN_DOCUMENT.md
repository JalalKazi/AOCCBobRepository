    # Solution Design Document (SDD)
    ## Daily RPA Bot Performance Reporting Automation - A360 Implementation

    ---

    ## Document Information & Overview

    **Document Title:** Solution Design Document - Daily RPA Bot Performance Reporting Automation  
    **Project:** Carhartt Reporting Bot  
    **Platform:** Automation Anywhere A360 (Cloud)  
    **Version:** 1.0 - Final  
    **Author:** Anima Lal  
    **Date:** June 16, 2026

    ### Reference Documents
    - Process Design Document (PDD) v1.0
    - Support Documentation v1.0
    - Technical Implementation Guide v1.0
    - Production Support Guide v1.0

    ---

    ## Executive Summary

    The Carhartt Reporting Bot automates daily consolidation of RPA bot execution reports, eliminating 2-3 hours of manual effort. Built on A360 platform, it processes emails, applies configurable logic rules, generates consolidated reports, and maintains historical data in SharePoint.

    **Key Metrics:**
    - **Execution:** Daily at 6:00 AM IST (Unattended)
    - **Duration:** 15-30 minutes
    - **Bots Processed:** 5-10 daily
    - **Success Rate Target:** 98%
    - **Time Savings:** 90% reduction in manual effort

    ---

    ## Architecture Overview

    ```
    Control Room (Cloud) → Bot Runner (On-Premise) → [Outlook + SharePoint + Excel]
    ```

    **Components:**
    1. **Report_Main** - Orchestrator bot
    2. **SubTask_Report** - Processor bot
    3. **Bot_Config.xlsx** - Configuration file
    4. **Master.xlsx** - Historical data (SharePoint)

    ---

    ## Detailed Technical Sections

    ### 1. Component Design

    #### Report_Main (Orchestrator)
    - **Purpose:** End-to-end workflow management
    - **Functions:** Config loading, email processing, SharePoint sync, notifications
    - **Execution Time:** 15-30 minutes
    - **Dependencies:** Bot_Config.xlsx, Outlook, SharePoint, SubTask_Report

    #### SubTask_Report (Processor)
    - **Purpose:** Individual bot report processing
    - **Functions:** File validation, data extraction, logic application, metric calculation
    - **Execution Time:** 2-5 minutes per bot
    - **Input Parameters:** 12 parameters (BotName, FolderPath, StatusColumn, LogicType, etc.)

    ---

    ### 2. Process Flow Summary

    **Main Flow:**
    1. Initialize → 2. Load Config → 3. Connect Outlook → 4. Download Files → 5. Process Reports → 6. Consolidate → 7. Update SharePoint → 8. Notify

    **SubTask Flow:**
    1. Initialize Counters → 2. Loop Files → 3. Apply Logic → 4. Update Daily Report

    ---

    ### 3. Logic Type Implementations

    #### Logic Type 1: Status
    ```
    IF CheckColumn empty OR has value:
    Volume++
    Status = lowercase(StatusColumn)
    IF Status contains "exception": Exception++
    ELSE IF Status = "success": Success++
    ELSE: Failure++
    ```

    #### Logic Type 2: KeywordCheck
    ```
    IF CheckColumn empty OR has value:
    Volume++
    Status = lowercase(StatusColumn)
    IF Status contains "parked": Success++
    ELSE: Exception++
    ```

    #### Logic Type 3: CMT
    ```
    IF CheckColumn empty OR has value:
    Volume++
    IF StatusColumn not empty: Success++
    ELSE: Exception++
    ```

    #### Logic Type 4: HeaderPR
    ```
    IF Loop = "H":
    Volume++
    IF Remark = "Success": Success++
    ELSE: Exception++
    ```

    #### Logic Type 5: RTLStatus
    ```
    Volume++
    TRY: StatusTemp = Status
    CATCH: StatusTemp = Exception
    StatusTemp = lowercase(StatusTemp)
    IF StatusTemp contains "released": Success++
    ELSE: Exception++
    ```

    #### Logic Type 6: CreditRisk
    ```
    IF CheckColumn empty OR has value:
    Volume++
    IF Status contains "L:\Credit Risk Matrix...": Success++
    ELSE: Exception++
    ```

    ---

    ### 4. Variable Management

    **Main Bot Variables (40+):**
    - **String:** bottime, LogFilePath, DailyFilepath, SharepointFolderLink, MainFile, Toemail, Report_date, BotName, FolderPath, StatusColumn, LogicType, etc.
    - **Number:** RetryCount (0-10), MaxRetry (10), MailFailure, RowsCount, NewRow
    - **DateTime:** TodayDate, yesterday, Endtime
    - **Boolean:** CopySuccess, PasteSuccess
    - **DataTable:** BotConfigDT, TGeneralConfig, TodayDT
    - **Record:** CurrentRow, TableRow
    - **Dictionary:** Email

    **SubTask Variables (30+):**
    - **Input:** BotName, FolderPath, StatusColumn, LogicType, CheckColumn, FileKeyword, LogFilePath, DailyFilepath, Report_date, MailFailure, MailRemarks, AllMailRemarks
    - **Local:** Volume, Success, Exception, Failure, Remark, Status, StatusTemp, filePath
    - **DataTable:** dtSummary
    - **Dictionary:** TodayFiles, currentRow

    ---

    ### 5. Exception Handling Framework

    **Global Level (Report_Main):**
    ```yaml
    TRY:
    [All execution steps]
    CATCH (BotException):
    - Log error with message and line number
    - Send failure email to stakeholders
    FINALLY:
    - Send completion email with log
    - Log execution completed
    ```

    **Retry Mechanism (SharePoint):**
    ```yaml
    RetryCount = 0, MaxRetry = 10
    WHILE (RetryCount < MaxRetry) AND (Success = False):
    TRY:
        [SharePoint operation]
        Success = True
    CATCH:
        RetryCount++
        Log retry attempt
        Wait 5 seconds
    ```

    **File Level (SubTask_Report):**
    ```yaml
    TRY:
    [Process file]
    CATCH:
    Log error
    Continue to next file (non-critical)
    ```

    ---

    ### 6. Key A360 Commands

    **Excel Operations:**
    - `Excel_MS.OpenSpreadsheet` - Open file (EDIT mode)
    - `Excel_MS.getWorksheetAsDataTable` - Read to DataTable
    - `Excel_MS.SetCell` - Write to cell
    - `Excel_MS.getNumberOfRows` - Get row count
    - `Excel_MS.CloseSpreadsheet` - Close and save

    **Email Operations:**
    - `Email.emailConnect` - Connect to Outlook
    - `Email.loop.iterators.email` - Read emails with filters
    - `Email.saveAttachment` - Save attachments
    - `Email.SendMailV2` - Send email with attachments

    **File Operations:**
    - `File.copyFiles` - Copy with overwrite
    - `File.deleteFiles` - Delete files
    - `File.loop.iterators.files` - Loop through files

    **Error Handling:**
    - `ErrorHandler.try` - Try block
    - `ErrorHandler.catch` - Catch exceptions
    - `ErrorHandler.finally` - Always execute

    ---

    ### 7. Security Design

    **Credential Management:**
    - Service account credentials in Windows Credential Manager
    - No hardcoded passwords in bot code
    - Windows integrated authentication for Outlook/SharePoint
    - Control Room vault for sensitive data (if needed)

    **Access Control:**
    - Bot runner service account with minimal required permissions
    - Read-only access to source bot reports
    - Read/Write access to SharePoint master file
    - Restricted access to configuration files

    **Data Security:**
    - No PII processed
    - Audit logs with 90-day retention
    - Encrypted communication (HTTPS to Control Room)
    - Secure file paths (no credentials in logs)

    ---

    ### 8. Logging & Monitoring

    **Log File Structure:**
    ```
    [2026-06-14 07:15:23] Report Bot Execution Started.
    [2026-06-14 07:15:25] Config file is opened
    [2026-06-14 07:15:30] Outlook is connected
    [2026-06-14 07:16:00] Subtask execution initiated for [BotName]
    [2026-06-14 07:21:20] Report Bot Execution completed.
    ```

    **Log Levels:**
    - **INFO:** Normal execution steps
    - **WARNING:** Non-critical issues (retries, missing files)
    - **ERROR:** Critical failures requiring intervention

    **Monitoring:**
    - Control Room execution history
    - Email notifications (success/failure)
    - Daily report validation
    - Weekly trend analysis

    ---

    ### 9. Application Integration

    **Outlook Integration:**
    - **Method:** COM Automation (Desktop client)
    - **Protocol:** MAPI/RPC
    - **Authentication:** Windows Integrated
    - **Operations:** Read emails, save attachments, send emails

    **SharePoint Integration:**
    - **Method:** File System (UNC path)
    - **Protocol:** SMB (Port 445)
    - **Authentication:** Windows Integrated
    - **Operations:** Read file, write file, create archive

    **Excel Integration:**
    - **Method:** COM Automation
    - **Protocol:** Local
    - **Authentication:** Not required
    - **Operations:** Open, read, write, close files

    ---

    ### 10. Performance Optimization

    **Techniques:**
    1. **DataTable Usage:** Read entire sheet once (10-20x faster than cell-by-cell)
    2. **Session Management:** Minimize open/close operations
    3. **Specific Sheet Selection:** Faster than active sheet
    4. **Disable Excel Features:** loadAddIns=false, excludeHiddenSheets=false
    5. **Retry Logic:** Handles transient failures without manual intervention

    **Benchmarks:**
    - Config loading: 30 seconds
    - Email processing: 2 minutes
    - Per-bot processing: 2-5 minutes
    - SharePoint sync: 5 minutes (with retries)
    - Total: 15-30 minutes

    ---

    ### 11. Deployment Plan

    **Environments:**
    1. **Development:** Local bot creator for development
    2. **UAT:** Test bot runner for validation
    3. **Production:** Production bot runner with schedule

    **Migration Steps:**
    1. Export bot from Dev Control Room
    2. Import to UAT Control Room
    3. Configure credentials in UAT
    4. Execute test runs (3-5 times)
    5. Validate output accuracy
    6. Export from UAT
    7. Import to Production
    8. Configure production credentials
    9. Set up schedule (6:00 AM daily)
    10. Monitor first week closely

    **Configuration:**
    - Service account setup
    - Folder structure creation
    - Bot_Config.xlsx population
    - Email distribution list
    - SharePoint permissions

    ---

    ### 12. Testing Strategy

    **Unit Testing:**
    - Test each logic type independently
    - Validate counter calculations
    - Test file validation logic
    - Test date calculations

    **Integration Testing:**
    - End-to-end execution with test data
    - Verify email processing
    - Validate SharePoint sync
    - Check notification emails

    **Error Testing:**
    - Missing configuration file
    - SharePoint unavailable
    - Outlook not connected
    - Corrupted Excel files
    - Missing input files

    **Test Data:**
    - Sample bot reports (5 bots)
    - Test email folder
    - Test SharePoint location
    - Mock configuration file

    ---

    ### 13. Known Limitations

    **Technical Constraints:**
    1. Single instance execution only (no parallel runs)
    2. Requires Outlook desktop client (no web version)
    3. SharePoint access via UNC path only (no API)
    4. Maximum 10 retry attempts for SharePoint
    5. Excel file size limit: 50MB per file

    **Business Constraints:**
    1. Report date is always yesterday (no custom dates)
    2. Email folder must be named "Report"
    3. Configuration changes require bot restart
    4. Manual intervention for critical failures
    5. 8x5 support coverage only

    ---

    ### 14. Risk Mitigation

    **Technical Risks:**
    - **SharePoint Unavailable:** Retry logic (10 attempts), alert on failure
    - **Outlook Connection Failure:** Pre-execution health check
    - **File Corruption:** Skip file, log error, continue
    - **Network Outage:** Schedule during stable hours, retry logic

    **Business Risks:**
    - **Source Bot Delays:** Buffer time in schedule (6:00 AM start)
    - **Report Format Changes:** Communicate changes 48 hours in advance
    - **Missing Reports:** Log warning, set counts to zero, notify

    **Mitigation Strategies:**
    - Comprehensive error handling
    - Retry mechanisms
    - Email notifications
    - Detailed logging
    - Support runbook

    ---

    ### 15. Support & Maintenance

    **Common Failure Scenarios:**
    1. **SharePoint Connection Failure:** Check network, verify permissions, retry
    2. **Outlook Not Connected:** Restart Outlook, verify profile loaded
    3. **Missing Input Files:** Check source bot execution, verify email keywords
    4. **Excel File Corruption:** Skip file, request resend from source bot
    5. **Configuration Missing:** Restore from backup

    **Troubleshooting:**
    - Check execution log for errors
    - Verify prerequisites (Outlook running, SharePoint accessible)
    - Review Control Room execution history
    - Validate configuration file
    - Test connectivity to external systems

    **Log Locations:**
    - Execution logs: `C:\RPAProcesses\Report_Bot\Audit_logs\`
    - Control Room logs: Available in web interface
    - Daily reports: `C:\RPAProcesses\Report_Bot\Daily_Report\`

    **Recovery Steps:**
    1. Identify failure point from logs
    2. Fix root cause
    3. Clean up partial outputs
    4. Rerun bot manually
    5. Validate success
    6. Document incident

    ---

    ### 16. Future Enhancements

    **Short-term (3-6 months):**
    - HTML formatted email notifications
    - Enhanced error categorization
    - Web-based configuration interface
    - Performance optimization (parallel processing)

    **Medium-term (6-12 months):**
    - Advanced analytics and dashboards
    - SharePoint API integration
    - Self-service stakeholder portal
    - ServiceNow integration

    **Long-term (12+ months):**
    - AI/ML for root cause analysis
    - Auto-remediation capabilities
    - Process mining integration
    - Enterprise-wide reporting platform

    ---

    ## Package Dependencies

    **Required A360 Packages:**
    - Excel_MS: 6.23.14
    - Email: 3.33.1
    - DataTable: 4.17.0
    - ErrorHandler: 2.13.0
    - File: 6.13.0
    - Folder: 6.13.0
    - String: 5.11.3
    - Number: 3.11.3
    - Datetime: 2.16.1
    - LogToFile: 3.10.0
    - Loop: 3.10.0
    - If: 3.7.14
    - TaskBot: 2.10.0
    - Application: 3.11.2
    - Delay: 3.9.1
    - Boolean: 2.13.2
    - Comment: 2.17.0
    - Step: 2.7.0
    - System: 3.17.0
    - Wait: 4.11.0
    - Window: 5.11.0

    ---

    ## Appendices

    ### Appendix A: Configuration File Structure

    **Bot_Config.xlsx - Sheet1:**
    | BotName | FolderPath | ArchivePath | StatusColumn | LogicType | CheckColumn | Keyword | FileKeyword |
    |---------|------------|-------------|--------------|-----------|-------------|---------|-------------|
    | Indirect PO | C:\RPA\Input\PO | C:\RPA\Archive\PO | Status | Status | | PO Report | PO_Summary |

    **Bot_Config.xlsx - General_Config:**
    | Parameter | Value |
    |-----------|-------|
    | Sharepoint Path | \\sharepoint\sites\RPA\Master.xlsx |
    | Email Addresses | user1@company.com; user2@company.com |
    | Main File Path | C:\RPA\Main_Report\Master.xlsx |

    ### Appendix B: Error Codes

    | Code | Description | Resolution |
    |------|-------------|------------|
    | ERR-001 | Config file not found | Verify file path |
    | ERR-002 | Outlook connection failed | Check Outlook running |
    | ERR-003 | SharePoint access denied | Verify permissions |
    | ERR-004 | File locked | Kill Excel processes |
    | ERR-005 | Invalid file format | Check extension |
    | ERR-006 | Column not found | Verify config |
    | ERR-007 | Disk space full | Free up space |
    | ERR-008 | Network timeout | Check connectivity |

    ### Appendix C: Glossary

    - **A360:** Automation Anywhere 360 platform
    - **Bot Runner:** Machine executing bot
    - **Control Room:** A360 management console
    - **DataTable:** In-memory table structure
    - **Logic Type:** Rule set for metric calculation
    - **Session:** Named connection to application
    - **SubTask:** Child bot called by parent
    - **UNC Path:** Universal Naming Convention path

    ---

    **Document Classification:** Internal - Confidential  
    **Distribution:** RPA Team, IT Operations, Business Stakeholders  
    **Next Review:** December 16, 2026  
    **Document Owner:** RPA Center of Excellence

    ---

    **END OF SOLUTION DESIGN DOCUMENT**