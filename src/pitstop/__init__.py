from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("pitstop-f1")
except PackageNotFoundError:
    __version__ = "unknown"
