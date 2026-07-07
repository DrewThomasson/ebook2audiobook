# ponytail: Audiobookshelf upload — POST finished m4b to a self-hosted ABS server

import os
import requests
from pathlib import Path


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
        except Exception:
            pass  # fall back to library-only request

    data = {"title": title or filename, "library": library_id}
    if author:
        data["author"] = author
    if folder_id:
        data["folder"] = folder_id

    try:
        with open(file_path, "rb") as f:
            resp = requests.post(
                url,
                headers=headers,
                files={"0": (filename, f, "audio/mp4")},
                data=data,
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
