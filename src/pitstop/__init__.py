from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("pitstop")
except PackageNotFoundError:
    __version__ = "unknown"
