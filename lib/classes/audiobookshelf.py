# ponytail: Audiobookshelf upload — POST finished m4b to a self-hosted ABS server

import json
import os
import requests
from pathlib import Path


def fetch_libraries(server_url: str, api_token: str) -> list[tuple[str, str]]:
    """Fetch available libraries from Audiobookshelf.

    Returns list of (name, id) tuples, or empty list on failure.
    """
    try:
        resp = requests.get(
            server_url.rstrip("/") + "/api/libraries",
            headers={"Authorization": f"Bearer {api_token}"},
            timeout=10,
        )
        if resp.ok:
            return [
                (lib["name"], lib["id"])
                for lib in resp.json().get("libraries", [])
                if lib.get("id")
            ]
        else:
            print(f"  ABS library fetch failed ({resp.status_code}): {resp.text[:200]}")
            return []
    except Exception as e:
        print(f"  ABS library fetch error: {e}")
        return []


def upload_to_abs(
    file_path: str,
    title: str,
    author: str,
    server_url: str,
    api_token: str,
    library_id: str,
    folder_id: str = "",
) -> bool:
    """Upload a single audiobook file to Audiobookshelf via its API.

    Returns True on success, prints error on failure.
    """
    if not os.path.isfile(file_path):
        print(f"  ABS upload skipped: file not found {file_path}")
        return False

    url = server_url.rstrip("/") + "/api/upload"
    headers = {"Authorization": f"Bearer {api_token}"}
    filename = Path(file_path).name

    # Auto-detect folder_id from library if not provided
    if not folder_id:
        try:
            lib_resp = requests.get(
                server_url.rstrip("/") + "/api/libraries",
                headers=headers,
                timeout=10,
            )
            if lib_resp.ok:
                libs = lib_resp.json().get("libraries", [])
                for lib in libs:
                    if lib.get("id") == library_id:
                        folders = lib.get("folders", [])
                        if folders:
                            folder_id = folders[0]["id"]
                        break
        except Exception as e:
            print(f"  ABS folder auto-detect failed: {e}")

    metadata = {"title": title or Path(file_path).stem, "libraryId": library_id}
    if author:
        metadata["author"] = author
    if folder_id:
        metadata["folderId"] = folder_id

    try:
        with open(file_path, "rb") as f:
            resp = requests.post(
                url,
                headers=headers,
                files={"file": (filename, f, "audio/mp4")},
                data={"metadata": json.dumps(metadata)},
                timeout=120,
            )
        if resp.ok:
            print(f"  Uploaded to Audiobookshelf: {filename}")
            return True
        else:
            print(f"  ABS upload failed ({resp.status_code}): {resp.text[:200]}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"  ABS upload failed: cannot connect to {server_url}")
        return False
    except requests.exceptions.Timeout:
        print(f"  ABS upload timed out after 120s: {filename}")
        return False
    except Exception as e:
        print(f"  ABS upload error: {e}")
        return False
