# check_auth.py
import google.auth

try:
    # This is the core command that performs the ADC search
    credentials, project_id = google.auth.default()

    print("✅ Authentication successful!")
    print("-" * 30)

    if hasattr(credentials, 'service_account_email'):
        print(f"🔑 Credential Type: Service Account")
        print(f"👤 Service Account Email: {credentials.service_account_email}")
    else:
        print(f"🔑 Credential Type: User Account (from gcloud login)")
        print(f"👤 User Email: {credentials.token_info.get('email', 'N/A')}")
        
    # The project_id returned here can sometimes be None if not explicitly set in the creds.
    # The quota_project_id is the one that really matters for APIs.
    if credentials.quota_project_id:
        print(f"🏢 Quota Project ID: {credentials.quota_project_id}")
    else:
        print("⚠️ Quota Project ID is not set in the credential file.")

except Exception as e:
    print("❌ Failed to find Application Default Credentials.")
    print(f"Error: {e}")