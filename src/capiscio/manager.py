import os
import sys
import hashlib
import platform
import stat
import shutil
import logging
import subprocess
from pathlib import Path
from typing import Optional, Tuple

import requests
from platformdirs import user_cache_dir
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()
logger = logging.getLogger(__name__)

# Configuration
CORE_VERSION = "2.6.0"  # The version of the core binary to download
GITHUB_REPO = "capiscio/capiscio-core"
BINARY_NAME = "capiscio"

def get_platform_info() -> Tuple[str, str]:
    """
    Determine the OS and Architecture.
    Returns: (os_name, arch_name)
    """
    system = platform.system().lower()
    machine = platform.machine().lower()

    # Normalize OS
    if system == "darwin":
        os_name = "darwin"
    elif system == "linux":
        os_name = "linux"
    elif system == "windows":
        os_name = "windows"
    else:
        raise RuntimeError(f"Unsupported operating system: {system}")

    # Normalize Architecture
    if machine in ("x86_64", "amd64"):
        arch_name = "amd64"
    elif machine in ("arm64", "aarch64"):
        arch_name = "arm64"
    else:
        raise RuntimeError(f"Unsupported architecture: {machine}")

    return os_name, arch_name

def get_binary_filename(os_name: str, arch_name: str) -> str:
    """Get the expected binary name for the platform."""
    ext = ".exe" if os_name == "windows" else ""
    return f"capiscio-{os_name}-{arch_name}{ext}"

def get_cache_dir() -> Path:
    """Get the directory where binaries are stored."""
    cache_dir = Path(user_cache_dir("capiscio", "capiscio")) / "bin"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir

def get_binary_path(version: str) -> Path:
    """Get the full path to the binary for a specific version."""
    os_name, arch_name = get_platform_info()
    filename = get_binary_filename(os_name, arch_name)
    # We might want to version the binary filename or put it in a versioned folder
    # For now, let's put it in a versioned folder
    return get_cache_dir() / version / filename

def _fetch_expected_checksum(version: str, filename: str) -> Tuple[Optional[str], str]:
    """Fetch the expected SHA-256 checksum from the release checksums.txt.

    Returns:
        A tuple of (checksum, status) where status is one of:
        - "ok"          — checksum found and returned
        - "fetch_failed" — could not download checksums.txt
        - "entry_missing" — checksums.txt downloaded but no entry for filename
    """
    url = f"https://github.com/{GITHUB_REPO}/releases/download/v{version}/checksums.txt"
    try:
        with requests.get(url, timeout=30) as resp:
            resp.raise_for_status()
            for line in resp.text.strip().splitlines():
                parts = line.split()
                if len(parts) == 2 and parts[1] == filename:
                    return parts[0], "ok"
            logger.warning(f"Binary {filename} not found in checksums.txt")
            return None, "entry_missing"
    except requests.exceptions.RequestException as e:
        logger.warning(f"Could not fetch checksums.txt: {e}")
        return None, "fetch_failed"

def _verify_checksum(file_path: Path, expected_hash: str) -> bool:
    """Verify SHA-256 checksum of a downloaded file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    actual = sha256.hexdigest()
    if actual != expected_hash:
        logger.error(f"Checksum mismatch: expected {expected_hash}, got {actual}")
        return False
    return True

def download_binary(version: str) -> Path:
    """
    Download the binary for the current platform and version.
    Returns the path to the executable.
    """
    os_name, arch_name = get_platform_info()
    filename = get_binary_filename(os_name, arch_name)
    target_path = get_binary_path(version)
    
    if target_path.exists():
        return target_path

    # Construct URL
    # Assuming standard GitHub release naming convention
    url = f"https://github.com/{GITHUB_REPO}/releases/download/v{version}/{filename}"
    
    console.print(f"[cyan]Downloading CapiscIO Core v{version} for {os_name}/{arch_name}...[/cyan]")
    
    try:
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            
            # Ensure directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                task = progress.add_task(f"Downloading...", total=total_size)
                
                with open(target_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        progress.update(task, advance=len(chunk))
        
        # Verify checksum BEFORE making executable (security: validate before trust)
        #
        # CAPISCIO_SKIP_CHECKSUM env var controls strict verification:
        #   When set to "1", "true", or "yes", checksum verification is skipped
        #   with a warning. By default, verification is required and will fail
        #   if checksums.txt cannot be fetched or the binary entry is missing.
        skip_checksum = os.environ.get("CAPISCIO_SKIP_CHECKSUM", "").lower() in ("1", "true", "yes")
        expected_hash, checksum_status = _fetch_expected_checksum(version, target_path.name)
        if expected_hash is not None:
            if not _verify_checksum(target_path, expected_hash):
                target_path.unlink()
                raise RuntimeError(
                    f"Binary integrity check failed for {target_path.name}. "
                    "The downloaded file does not match the published checksum. "
                    "This may indicate a tampered or corrupted download."
                )
            logger.info(f"Checksum verified for {target_path.name}")
        elif skip_checksum:
            if checksum_status == "fetch_failed":
                logger.warning(
                    "Could not verify binary integrity (checksums.txt not available). "
                    "Skipping verification (CAPISCIO_SKIP_CHECKSUM=true)."
                )
            else:
                logger.warning(
                    f"Could not verify binary integrity (no entry for {target_path.name} in checksums.txt). "
                    "Skipping verification (CAPISCIO_SKIP_CHECKSUM=true)."
                )
        else:
            target_path.unlink()
            if checksum_status == "fetch_failed":
                raise RuntimeError(
                    f"Checksum verification failed: checksums.txt could not be fetched for v{version}. "
                    "Cannot verify binary integrity. "
                    "Set CAPISCIO_SKIP_CHECKSUM=true to bypass."
                )
            else:
                raise RuntimeError(
                    f"Checksum verification failed: no entry for {target_path.name} in v{version} checksums.txt. "
                    "Cannot verify binary integrity. "
                    "Set CAPISCIO_SKIP_CHECKSUM=true to bypass."
                )

        # Make executable only after checksum verification passes
        st = os.stat(target_path)
        os.chmod(target_path, st.st_mode | stat.S_IEXEC)
        
        console.print(f"[green]Successfully installed CapiscIO Core v{version}[/green]")
        return target_path
        
    except requests.exceptions.RequestException as e:
        if target_path.exists():
            target_path.unlink()
        raise RuntimeError(f"Failed to download binary from {url}: {e}")
    except Exception as e:
        if target_path.exists():
            target_path.unlink()
        raise RuntimeError(f"Failed to install binary: {e}")

def run_core(args: list[str]) -> int:
    """
    Ensure binary exists and run it with provided args.
    Returns exit code.
    """
    try:
        binary_path = download_binary(CORE_VERSION)
        
        # Replace the current process with the binary
        # This is cleaner than subprocess for a wrapper
        if platform.system() == "Windows":
            return subprocess.call([str(binary_path)] + args)
        else:
            os.execv(str(binary_path), [str(binary_path)] + args)
            return 0 # Should not be reached
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        return 1
