# Azure Storage integration
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE.md)&nbsp;
[![fr](https://img.shields.io/badge/lang-fr-yellow.svg)](README-fr.md)  

This integration allows to interact with Azure Blob Storage from Visual TOM Jobs or Resources.
Several interactions are available:
  * Download
  * Upload
  * List (to check if a file is present)

# Disclaimer
No Support and No Warranty are provided by Absyss SAS for this project and related material. The use of this project's files is at your own risk.

Absyss SAS assumes no liability for damage caused by the usage of any of the files offered here via this Github repository.

Consultings days can be requested to help for the implementation.

# Prerequisites

  * Visual TOM 7.1 or greater
  * Python 3.x installed on your agent
  * Azure Storage account with a Blob container created
  * Install the required Python packages using pip:
    ```bash
    pip install -r requirements.txt
    ```
  * Unix Agent (Windows usage will be available later)

# Instructions

  * Create an Azure Application and set the following environment variables in config.py in the same folder (a template is available in the repository):
    * `AZURE_CLIENT_ID`: Client ID of your Azure Active Directory application
    * `AZURE_TENANT_ID`: Tenant ID of your Azure Active Directory
    * `AZURE_CLIENT_SECRET`: Client secret of your Azure Active Directory application
    * `AZURE_STORAGE_NAME`: Name of the Azure Storage account
  * Create in Visual TOM a "Custom Application" connection with the following definition:
    ![Custom application screenshot](screenshots/Azure_Storage_CustomApplication.png?raw=true)

When used in a Job, 2 actions are available:
  * Download a file from Azure Storage Container to local folder
  * Upload a file from local folder to Azure Storage Container

When used in a generic Resource:
  * List to check if files are present in the container

Description of parameters (case sensitive):
  * `Container name`: Name of the storage container
  * `Type of transfer`: Download, Upload or List
  * `Local path`: Folder (Absolute path) where the file is present or will be downloaded. Required for Download and Upload.
  * `Remote path`: Optional. Path where the file is present in the container or where it will be stored.
  * `Filename`: Name of the file(s) to manage. This value accepts "Unix-Like" expressions
  * `Overwrite`: Specify what happens if a file is already present in the destination (default: Overwrite)
  * `Error if no file found`: Specify what happens if there is no file to Upload/Download (default: Error)

When used in the generic Resource, the definition is:
  * `Batch queue`: queue_azstorage
  * `Script`: #
  * `Parameter #1`: Name of the container
  * `Parameter #2`: List
  * `Parameter #3`: Remote path (optional)
  * `Parameter #4`: Filename (can include "Unix-Like" expressions)

The integration returns specific codes for errors:
  * 90: Inconsistent parameters
  * 91: No file found and "Error if no file found" enabled or Type of transfer = List
  * 92: At least 1 file has not been transfered due to already existing file and "Overwrite" disabled
  * 99: Unknown exception catched by the script

# License
This project is licensed under the Apache 2.0 License - see the [LICENSE](license) file for details


# Code of Conduct
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-v2.1%20adopted-ff69b4.svg)](code-of-conduct.md)  
Absyss SAS has adopted the [Contributor Covenant](CODE_OF_CONDUCT.md) as its Code of Conduct, and we expect project participants to adhere to it. Please read the [full text](CODE_OF_CONDUCT.md) so that you can understand what actions will and will not be tolerated.
