import argparse
from azure.storage.blob import BlobServiceClient
from azure.identity import ClientSecretCredential
from config import *
import os, time, re
import glob

#####################################################
### Function to print messages to the standard output
#####################################################
def printFormat(typeMessage: str, Content:str):
	timestamp=(time.strftime("%H:%M:%S", time.localtime()))
	print(timestamp + ' | ' + typeMessage.ljust(7) + ' | ' + Content)
	return;

#####################################################
### Managing parameters
#####################################################
# Parse command line arguments
parser = argparse.ArgumentParser(description='Azure Blob Storage Transfer')
parser.add_argument('--transfer_type', choices=['Upload', 'Download', 'List'], help='Action type: Upload, Download or List', required=True)
parser.add_argument('--container_name', help='Azure Blob container name', required=True)
parser.add_argument('--local_path', help='Local file path', required=False)  # Required for both upload and download because VTOM does not handle relative paths
parser.add_argument('--remote_path', help='Remote file path', default='', required=False)
parser.add_argument('--filename', help='Filename to be transferred', required=True)
parser.add_argument('--overwrite', choices=['Yes', 'No'], help='Overwrite if target file is already present', required=False, default='Yes')
parser.add_argument('--error_no_file', choices=['Yes', 'No'], help='Fail if no file is found', required=False, default='Yes')
args = parser.parse_args()

# Check if the local path is set and exists when uploading or downloading
if args.transfer_type in ['Upload', 'Download']:
    if args.local_path == '':
        printFormat("ERROR","Local path is not set. Exiting in error.")
        exit(90)
    if not os.path.exists(args.local_path):
        printFormat("ERROR","Local path does not exist. Exiting in error.")
        exit(90)

    printFormat("INFO", f"Arguments:")
    printFormat("INFO", f"  - Transfer type: {args.transfer_type}")
    printFormat("INFO", f"  - Container name: {args.container_name}")
    printFormat("INFO", f"  - Local path: {args.local_path}")
    if args.remote_path:
        printFormat("INFO", f"  - Remote path: {args.remote_path}")
    else:
        printFormat("INFO", f"  - Remote path: Not set")
    printFormat("INFO", f"  - Filename: {args.filename}")
    printFormat("INFO", f"  - Overwrite: {args.overwrite}")
    printFormat("INFO", f"  - Error if no file: {args.error_no_file}")
else:
    printFormat("INFO", f"Arguments:")
    printFormat("INFO", f"  - Transfer type: {args.transfer_type}")
    printFormat("INFO", f"  - Container name: {args.container_name}")
    if args.remote_path:
        printFormat("INFO", f"  - Remote path: {args.remote_path}")
    else:
        printFormat("INFO", f"  - Remote path: Not set")
    printFormat("INFO", f"  - Filename: {args.filename}")

print("")
printFormat("INFO", f"Start processing...")
#####################################################
### Connection to Azure Blob Storage account
#####################################################
# Connect to Azure Blob Storage account
token_credential = ClientSecretCredential(AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)
blob_service_client = BlobServiceClient(account_url=f"https://{AZURE_STORAGE_NAME}.blob.core.windows.net", credential=token_credential)

# Create a Blob client for the specified container
container_client  = blob_service_client.get_container_client(container=args.container_name)

#####################################################
### Upload actions
#####################################################
if args.transfer_type == 'Upload':
    error_found = False
    try:
        # Check if file exists in the local path
        files = glob.glob(os.path.join(args.local_path,args.filename))
        if len(files) == 0:
            if args.error_no_file == 'Yes':
                printFormat("ERROR","No file found matching the pattern. Exiting in error.")
                exit(91)
            else:
                printFormat("INFO","No file found matching the pattern. Exiting.")
                exit(0)

        # Loop through the list of files found on local path
        for local_filename in files:
            file_found = False

            remote_filename = os.path.join(args.remote_path,os.path.basename(local_filename))
            filename = os.path.basename(local_filename)

            if args.overwrite == 'Yes':
                with open(local_filename, "rb") as local_file_content:
                    container_client.upload_blob(name=filename, data=local_file_content, overwrite=True)
                    printFormat("SUCCESS", f"'{local_filename}' has been successfully moved to Azure Blob Storage container '{args.container_name}'.")
            else:
                # Check if the file already exists in the container
                blob_list = container_client.list_blobs(name_starts_with=remote_filename)
                for blob in blob_list:
                    if blob.name == remote_filename:
                        file_found = True

                if not file_found:
                    with open(local_filename, "rb") as local_file_content:
                        container_client.upload_blob(name=filename, data=local_file_content, overwrite=False)
                        printFormat("SUCCESS", f"'{remote_filename}' has been successfully moved to Azure Blob Storage container '{args.container_name}'.")
                else:
                    printFormat("ERROR", f"'{remote_filename}' already exists in the Azure Blob Storage container. Skipping file...")
                    error_found = True
        
        if error_found:
            printFormat("ERROR", f"Some files were not uploaded due to existing files in the Azure Blob Storage container '{args.container_name}'.")
            exit(92)
        else:
            printFormat("SUCCESS", f"All files have been successfully uploaded to Azure Blob Storage container '{args.container_name}'.")
    except Exception as e:
        printFormat("ERROR", f"An error occurred while uploading the file: {e}")
        exit(99)

#####################################################
### Download actions
#####################################################
elif args.transfer_type == 'Download':
    error_found = False
    file_found = False
    try:
        blob_list = container_client.list_blobs(name_starts_with=args.remote_path)
        for blob in blob_list:
            # Test if the blob name matches the pattern via regular expression (expression are Unix like, converted to regex)
            pattern = re.escape(os.path.join(args.remote_path,args.filename)).replace("\\*", ".*").replace("\\?", ".")
            if re.match(pattern, blob.name):
                file_found = True
                # Test if the file already exists in the local path otherwise download can be done
                if os.path.exists(os.path.join(args.local_path,os.path.basename(blob.name))) and args.overwrite == 'No':
                    printFormat("ERROR", f"'{blob.name}' already exists in the local path. Skipping file...")
                    error_found = True
                else:
                    blob_client = blob_service_client.get_blob_client(container=args.container_name, blob=blob.name)
                    with open(file=os.path.join(args.local_path,os.path.basename(blob.name)), mode="wb") as local_file:
                        download_stream = blob_client.download_blob()
                        local_file.write(download_stream.readall())
                    printFormat("SUCCESS", f"'{blob.name}' has been successfully downloaded to '{args.local_path}'.")
        if error_found:
            printFormat("ERROR", f"Some files were not downloaded due to existing files in the local path.")
            exit(92)
        
        if not file_found:
            if args.error_no_file == 'Yes':
                printFormat("ERROR", f"No file found matching the pattern '{os.path.join(args.remote_path,args.filename)}' in the Azure Blob Storage container '{args.container_name}'.")
                exit(91)
            else:
                printFormat("INFO", f"No file found matching the pattern '{os.path.join(args.remote_path,args.filename)}' in the Azure Blob Storage container '{args.container_name}'.")
                exit(0)
        else:
            printFormat("SUCCESS", f"All files have been successfully downloaded to '{args.local_path}'.")
    except Exception as e:
        printFormat("ERROR", f"An error occurred while downloading the file: {e}")
        exit(99)

#####################################################
### List actions (for resources mostly)
#####################################################
elif args.transfer_type == 'List':
    file_found = False
    try:
        # List all blobs in the container and check if at least one matches the pattern from filename argument
        blob_list = container_client.list_blobs(name_starts_with=args.remote_path)
        for blob in blob_list:
            # Test if the blob name matches the pattern via regular expression (expression are Unix like, converted to regex)
            pattern = re.escape(os.path.join(args.remote_path,args.filename)).replace("\\*", ".*").replace("\\?", ".")
            if re.match(pattern, blob.name):
                printFormat("SUCCESS", f"'{blob.name}' is present in the container '{args.container_name}'.")
                file_found = True
        if not file_found:
            printFormat("ERROR", f"No file found matching the pattern '{os.path.join(args.remote_path,args.filename)}' in the Azure Blob Storage container '{args.container_name}'.")
            exit(91)
    except Exception as e:
        printFormat("ERROR", f"An error occurred while listing the files: {e}")
        exit(99)