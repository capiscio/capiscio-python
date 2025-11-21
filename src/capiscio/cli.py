import sys
import shutil
from rich.console import Console
from capiscio.manager import run_core, get_cache_dir

console = Console()

def main():
    """
    Main entry point for the CapiscIO CLI wrapper.
    
    This wrapper manages the download and execution of the platform-specific
    capiscio-core binary.
    """
    args = sys.argv[1:]
    
    # Handle wrapper-specific maintenance commands
    if len(args) > 0:
        if args[0] == "--wrapper-clean":
            try:
                cache_dir = get_cache_dir()
                if cache_dir.exists():
                    shutil.rmtree(cache_dir)
                    console.print(f"[green]Cleaned cache directory:[/green] {cache_dir}")
                else:
                    console.print("[yellow]Cache directory does not exist.[/yellow]")
                sys.exit(0)
            except Exception as e:
                console.print(f"[red]Failed to clean cache:[/red] {e}")
                sys.exit(1)
                
        elif args[0] == "--wrapper-version":
            from importlib.metadata import version
            try:
                v = version("capiscio")
                console.print(f"capiscio-python wrapper v{v}")
            except Exception:
                console.print("capiscio-python wrapper (unknown version)")
            # We don't exit here, we let it fall through to core so core can print its version too if needed
            # But usually --version is exclusive. Let's just exit.
            sys.exit(0)

    # Delegate to the core binary
    sys.exit(run_core(args))

if __name__ == "__main__":
    main()
