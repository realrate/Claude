"""Download seal post images and captions from Google Drive.

Usage:
    python scripts/pull_seal_posts.py --industry us_air --output-dir output/us_air/2026

Authenticates with a Google service account and downloads matching files
from the shared seal posts Drive folder.

Environment:
    GOOGLE_SERVICE_ACCOUNT_KEY — path to service account JSON key file,
                                  or the raw JSON content itself
"""
import argparse
import io
import json
import os
import re
import sys

# # Drive folder ID containing seal post assets
DRIVE_FOLDER_ID = "1i1m4hsmOKzYrXrsPYxGrtuwMMOrQHH2T"


def get_credentials():
    """Load Google service account credentials from env var."""
    key_source = os.environ.get("GOOGLE_SERVICE_ACCOUNT_KEY", "")
    if not key_source:
        print("ERROR: GOOGLE_SERVICE_ACCOUNT_KEY not set")
        sys.exit(1)

    from google.oauth2 import service_account

    # # If it's a file path, load from file; otherwise parse as raw JSON
    if os.path.isfile(key_source):
        return service_account.Credentials.from_service_account_file(
            key_source,
            scopes=["https://www.googleapis.com/auth/drive.readonly"],
        )
    else:
        info = json.loads(key_source)
        return service_account.Credentials.from_service_account_info(
            info,
            scopes=["https://www.googleapis.com/auth/drive.readonly"],
        )


def build_drive_service(credentials):
    """Build Google Drive API v3 service."""
    from googleapiclient.discovery import build
    return build("drive", "v3", credentials=credentials)


def list_folder_contents(service, folder_id):
    """List all files in a Drive folder (non-recursive)."""
    files = []
    page_token = None
    while True:
        response = service.files().list(
            q="'%s' in parents and trashed = false" % folder_id,
            fields="nextPageToken, files(id, name, mimeType)",
            pageToken=page_token,
            pageSize=100,
        ).execute()
        files.extend(response.get("files", []))
        page_token = response.get("nextPageToken")
        if not page_token:
            break
    return files


def download_file(service, file_id):
    """Download a file's content from Drive."""
    from googleapiclient.http import MediaIoBaseDownload
    request = service.files().get_media(fileId=file_id)
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    buffer.seek(0)
    return buffer.read()


def slug_from_industry(industry):
    """Convert industry slug to human-readable folder name patterns.

    us_air → ['US Air', 'us_air', 'US_Air', 'Air']
    """
    clean = industry.replace("us_", "")
    return [
        "US " + clean.title(),
        industry,
        "US_" + clean.title(),
        clean.title(),
        clean,
    ]


def find_subfolder(files, industry):
    """Find a subfolder matching the industry name (Layout A)."""
    patterns = slug_from_industry(industry)
    for f in files:
        if f["mimeType"] == "application/vnd.google-apps.folder":
            for pattern in patterns:
                if f["name"].lower() == pattern.lower():
                    return f
    return None


def match_flat_files(files, industry):
    """Match files by prefix naming convention (Layout B)."""
    prefix_patterns = slug_from_industry(industry)
    matched = []
    for f in files:
        if f["mimeType"] == "application/vnd.google-apps.folder":
            continue
        name_lower = f["name"].lower()
        for prefix in prefix_patterns:
            if name_lower.startswith(prefix.lower() + "_"):
                matched.append(f)
                break
    return matched


def extract_company_slug(filename, industry):
    """Extract company slug from seal post filename.

    seal_company_name.png → company_name
    us_air_company_name_seal.png → company_name
    """
    # # Pattern: seal_<company>.png
    m = re.match(r"seal_(.+)\.png$", filename, re.IGNORECASE)
    if m:
        return m.group(1).lower().replace(" ", "_")

    # # Pattern: <prefix>_<company>_seal.png
    for prefix in slug_from_industry(industry):
        pattern = re.escape(prefix) + r"_(.+?)_seal\.png$"
        m = re.match(pattern, filename, re.IGNORECASE)
        if m:
            return m.group(1).lower().replace(" ", "_")

    # # Fallback: strip extension and use full name
    base = os.path.splitext(filename)[0].lower().replace(" ", "_")
    return base


def main():
    parser = argparse.ArgumentParser(description="Download seal posts from Google Drive")
    parser.add_argument("--industry", required=True, help="Industry slug e.g. us_air")
    parser.add_argument("--output-dir", required=True, help="Directory to save downloaded files")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    credentials = get_credentials()
    service = build_drive_service(credentials)

    print("Listing Drive folder contents...")
    root_files = list_folder_contents(service, DRIVE_FOLDER_ID)

    # # Try Layout A: look for a subfolder matching the industry
    subfolder = find_subfolder(root_files, args.industry)
    if subfolder:
        print("Found subfolder: %s" % subfolder["name"])
        seal_files = list_folder_contents(service, subfolder["id"])
    else:
        # # Layout B: match files by prefix in the root folder
        print("No subfolder found, trying flat file matching...")
        seal_files = match_flat_files(root_files, args.industry)

    if not seal_files:
        print("No seal post files found for industry: %s" % args.industry)
        print(json.dumps({"downloaded": []}))
        return

    # # Separate images and captions
    images = [f for f in seal_files if f["name"].lower().endswith((".png", ".jpg", ".jpeg"))]
    captions = [f for f in seal_files if f["name"].lower().endswith(".txt")]

    downloaded = []

    for img_file in images:
        company_slug = extract_company_slug(img_file["name"], args.industry)
        print("Downloading: %s → seal_%s.png" % (img_file["name"], company_slug))

        # # Download image
        img_data = download_file(service, img_file["id"])
        img_out = os.path.join(args.output_dir, "seal_%s.png" % company_slug)
        with open(img_out, "wb") as f:
            f.write(img_data)

        # # Find matching caption file
        caption_out = os.path.join(args.output_dir, "seal_%s_caption.txt" % company_slug)
        caption_found = False
        for cap_file in captions:
            cap_name = cap_file["name"].lower()
            if company_slug.replace("_", " ") in cap_name or company_slug in cap_name:
                print("  Caption: %s" % cap_file["name"])
                cap_data = download_file(service, cap_file["id"])
                with open(caption_out, "wb") as f:
                    f.write(cap_data)
                caption_found = True
                break

        downloaded.append({
            "company": company_slug,
            "image": img_out,
            "caption": caption_out if caption_found else None,
        })

    print("\nDownloaded %d seal post(s)" % len(downloaded))
    # # Print JSON summary for the orchestrator to parse
    print(json.dumps({"downloaded": downloaded}))


if __name__ == "__main__":
    main()
