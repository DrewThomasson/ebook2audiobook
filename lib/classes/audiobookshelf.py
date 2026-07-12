import os
import requests
from pathlib import Path


def fetch_libraries(server_url: str, api_token: str) -> list[tuple[str, str]]:
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


MIME_MAP: dict = {
    ".m4b": "audio/mp4",
    ".m4a": "audio/mp4",
    ".mp4": "audio/mp4",
    ".mp3": "audio/mpeg",
    ".flac": "audio/flac",
    ".ogg": "audio/ogg",
    ".wav": "audio/wav",
    ".aac": "audio/aac",
    ".opus": "audio/opus",
}


def _detect_folder_id(server_url: str, headers: dict, library_id: str) -> str:
    try:
        lib_resp = requests.get(
            server_url.rstrip("/") + "/api/libraries",
            headers=headers,
            timeout=10,
        )
        if lib_resp.ok:
            for lib in lib_resp.json().get("libraries", []):
                if lib.get("id") == library_id:
                    folders = lib.get("folders", [])
                    if folders:
                        return folders[0]["id"]
    except Exception as e:
        print(f"  ABS folder auto-detect failed: {e}")
    return ""


def upload_to_abs(
    file_path: str | list[str],
    title: str,
    author: str,
    server_url: str,
    api_token: str,
    library_id: str,
    folder_id: str = "",
) -> tuple[bool, str]:
    if isinstance(file_path, str):
        file_path = [file_path]
    existing: list[str] = [f for f in file_path if os.path.isfile(f)]
    if not existing:
        print(f"  ABS upload skipped: no valid files in {file_path}")
        return (False, 'No valid files to upload')
    url: str = server_url.rstrip("/") + "/api/upload"
    headers: dict = {"Authorization": f"Bearer {api_token}"}
    if not folder_id:
        folder_id = _detect_folder_id(server_url, headers, library_id)
    form_data: dict = {
        "title": title or Path(existing[0]).stem,
        "library": library_id,
        "folder": folder_id,
    }
    if author:
        form_data["author"] = author
    files_dict: dict = {}
    handles: list = []
    try:
        for i, fp in enumerate(existing):
            fh = open(fp, "rb")
            handles.append(fh)
            mime_type: str = MIME_MAP.get(Path(fp).suffix.lower(), "audio/mp4")
            files_dict[str(i)] = (Path(fp).name, fh, mime_type)
        resp = requests.post(
            url,
            headers=headers,
            files=files_dict,
            data=form_data,
            timeout=300,
        )
        if resp.ok:
            names: str = ", ".join(Path(f).name for f in existing)
            print(f"  Uploaded to Audiobookshelf: {names}")
            return (True, f'Uploaded: {names}')
        else:
            print(f"  ABS upload failed ({resp.status_code}): {resp.text[:200]}")
            return (False, f'HTTP {resp.status_code}: {resp.text[:200]}')
    except requests.exceptions.ConnectionError:
        print(f"  ABS upload failed: cannot connect to {server_url}")
        return (False, f'Cannot connect to {server_url}')
    except requests.exceptions.Timeout:
        print(f"  ABS upload timed out after 300s")
        return (False, 'Upload timed out after 300s')
    except Exception as e:
        print(f"  ABS upload error: {e}")
        return (False, str(e))
    finally:
        for fh in handles:
            fh.close()
