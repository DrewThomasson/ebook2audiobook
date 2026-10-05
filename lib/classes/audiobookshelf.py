import os
import requests
from pathlib import Path
from lib.lang import legends


def fetch_libraries(server_url:str, api_token:str)->list[tuple[str, str]]:
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
            error = legends['error_abs_fetch_failed'].format(code=resp.status_code, text=resp.text[:200])
            print(error)
            return []
    except Exception as e:
        error = legends['error_abs_fetch'].format(e=f'{type(e).__name__}: {e}')
        print(error)
        return []


MIME_MAP:dict = {
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


def _detect_folder_id(server_url:str, headers:dict, library_id:str)->str:
    try:
        lib_resp = requests.get(
            server_url.rstrip("/") + "/api/libraries",
            headers=headers,
            timeout=10,
        )
        if not lib_resp.ok:
            error = legends['error_abs_folder_detect_http'].format(code=lib_resp.status_code, text=lib_resp.text[:200])
            print(error)
            return ""
        for lib in lib_resp.json().get("libraries", []):
            if lib.get("id") == library_id:
                folders = lib.get("folders", [])
                if folders:
                    return folders[0].get("id", "")
                error = legends['error_abs_no_folders'].format(id=library_id)
                print(error)
                return ""
        error = legends['error_abs_lib_not_on_server'].format(id=library_id)
        print(error)
    except Exception as e:
        error = legends['error_abs_folder_detect'].format(e=f'{type(e).__name__}: {e}')
        print(error)
    return ""


def upload_to_abs(
    file_path:str|list[str],
    title:str,
    author:str,
    server_url:str,
    api_token:str,
    library_id:str,
    folder_id:str = "",
    timeout:int = 1800,
)->tuple[bool, str]:
    if isinstance(file_path, str):
        file_path = [file_path]
    existing:list[str] = [f for f in file_path if os.path.isfile(f)]
    if not existing:
        msg = legends['msg_abs_skip_no_files'].format(files=file_path)
        print(msg)
        return (False, legends['msg_abs_no_valid_files'])
    if not library_id:
        msg = legends['msg_abs_skip_no_library']
        print(msg)
        return (False, legends['msg_abs_no_library'])
    url:str = server_url.rstrip("/") + "/api/upload"
    headers:dict = {"Authorization": f"Bearer {api_token}"}
    if not folder_id:
        folder_id = _detect_folder_id(server_url, headers, library_id)
    if not folder_id:
        msg = legends['msg_abs_skip_no_folder']
        print(msg)
        return (False, legends['msg_abs_no_folder'])
    total_bytes:int = sum(os.path.getsize(f) for f in existing)
    form_data:dict = {
        "title": title or Path(existing[0]).stem,
        "library": library_id,
        "folder": folder_id,
    }
    if author:
        form_data["author"] = author
    files_dict:dict = {}
    handles:list = []
    try:
        for i, fp in enumerate(existing):
            fh = open(fp, "rb")
            handles.append(fh)
            mime_type:str = MIME_MAP.get(Path(fp).suffix.lower(), "audio/mp4")
            files_dict[str(i)] = (Path(fp).name, fh, mime_type)
        print(legends['msg_abs_uploading'].format(count=len(existing), size=f'{total_bytes / 1048576:.1f}', url=url))
        resp = requests.post(
            url,
            headers=headers,
            files=files_dict,
            data=form_data,
            timeout=(30, timeout),
        )
        if resp.ok:
            names:str = ", ".join(Path(f).name for f in existing)
            msg = legends['msg_abs_uploaded'].format(names=names)
            print(msg)
            return (True, legends['msg_abs_uploaded_short'].format(names=names))
        else:
            error = legends['error_abs_upload_http'].format(code=resp.status_code, text=resp.text[:200])
            print(error)
            return (False, f'HTTP {resp.status_code}: {resp.text[:200]}')
    except requests.exceptions.ConnectTimeout as e:
        error = legends['error_abs_connect_timeout'].format(url=server_url)
        print(error)
        return (False, legends['error_abs_connect_timeout_short'].format(url=server_url))
    except requests.exceptions.ReadTimeout as e:
        error = legends['error_abs_read_timeout'].format(timeout=timeout)
        print(error)
        return (False, legends['error_abs_read_timeout_short'].format(timeout=timeout))
    except requests.exceptions.ConnectionError as e:
        # ConnectionError covers refused, reset, and broken pipe. The cause
        # matters: refused means nothing is listening, reset means the server
        # accepted the upload then dropped it (size limit, proxy, crash).
        cause = str(e)
        if 'Connection refused' in cause or 'NewConnectionError' in cause:
            hint = legends['msg_abs_hint_refused']
        elif 'reset' in cause.lower() or 'BrokenPipe' in cause or 'RemoteDisconnected' in cause:
            hint = legends['msg_abs_hint_reset']
        else:
            hint = legends['msg_abs_hint_conn']
        error = legends['error_abs_upload_conn'].format(hint=hint, e=f'{type(e).__name__}: {cause[:300]}')
        print(error)
        return (False, f'{hint}: {cause[:200]}')
    except Exception as e:
        error = legends['error_abs_upload'].format(e=f'{type(e).__name__}: {e}')
        print(error)
        return (False, f'{type(e).__name__}: {e}')
    finally:
        for fh in handles:
            fh.close()
