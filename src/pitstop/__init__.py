from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("pitstop")
except PackageNotFoundError:
    __version__ = "unknown"
