# DFIR Case Management Tool

A batch script utility for creating and archiving digital forensics cases with standardized folder structures.

## Features

- **Case Creation**:
  - Creates standardized folder structure for new cases
  - Generates empty Keywords.txt file
  - Opens case folder in Explorer upon creation

- **Case Archiving**:
  - Interactive folder selection
  - ZIP archive creation with PowerShell
  - Option to delete original folder after archiving

- **Configuration**:
  - Persistent backup location storage (in `case_config.txt`)
  - Interactive folder browser for location selection
  - Location verification

## Requirements

- Windows 7 or later
- PowerShell 5.1 or later
- Administrative privileges recommended for file operations

## Usage

1. Run the batch file
2. Main menu options:
   - `1` Create new case
     - Prompts for case name
     - Creates folder structure:
       ```
       CaseName/
       ├── 01 - Evidence/
       ├── 02 - Case/
       ├── 03 - Malware/
       ├── 03 - Extracted Evidence/
       └── Keywords.txt
       ```
   - `2` Archive existing case
     - Lists available folders
     - Creates ZIP archive in selected location
     - Optionally deletes original folder
   - `3` Change backup location
     - Interactive folder browser
     - Saves location to config file
   - `0` Exit

## Configuration

The tool maintains configuration in `case_config.txt` containing:
- Primary backup location path

## Version

Current version: 0.2

## 👤 Author

**Jacob Wilson**  
📧 dfirvault@gmail.com
[https://www.linkedin.com/in/jacob--wilson/](https://www.linkedin.com/in/jacob--wilson/)

## Notes

- First run will prompt for backup location configuration
- Uses PowerShell for advanced file operations
- Archived cases use the original folder name with `.zip` extension
- Case folders are created in the current working directory

## Changelog

### v0.2
- Added persistent configuration
- Improved backup location handling
- Enhanced archive functionality

### v0.1
- Initial release
- Basic case creation and archiving
