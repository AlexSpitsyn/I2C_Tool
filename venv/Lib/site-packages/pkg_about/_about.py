# Copyright (c) 2020-2022 Adam Karpierz
# Licensed under the zlib/libpng License
# https://opensource.org/licenses/Zlib

__all__ = ('about',)


def about(package=None, *, metadata=None):
    import sys
    from packaging.version import parse as parse_version
    from importlib_metadata import metadata as get_metadata
    pkg_globals = sys._getframe(1).f_globals
    pkg_globals.pop("__builtins__", None)
    pkg_globals.pop("__cached__",   None)
    if metadata is None:
        if package is None: package = pkg_globals["__package__"]
        metadata = get_metadata(package)
    version = parse_version(metadata["Version"])
    release_levels = dict(a="alpha", b="beta", rc="candidate",
                          dev="dev", post="post", local="local",
                          final="final",)
    pkg_metadata = dict(
        __title__        = metadata["Name"],
        __summary__      = metadata.get("Summary"),
        __uri__          = metadata.get("Home-page"),
        __version__      = str(version),
        __version_info__ = type("version_info", (), dict(
                               major=version.major,
                               minor=version.minor,
                               micro=version.micro,
                               releaselevel=release_levels[
                                   version.pre[0] if version.pre else
                                   "dev"   if version.dev   else
                                   "post"  if version.post  else
                                   "local" if version.local else
                                   "final"],
                               serial=(version.pre[1] if version.pre else
                                       version.dev or version.post or
                                       version.local or 0))),
        __author__       = metadata.get("Author"),
        __maintainer__   = metadata.get("Maintainer"),
        __email__        = metadata.get("Author-email"),
        __license__      = metadata.get("License"),
        __copyright__    = metadata.get("Copyright")  # for now is None
    )
    pkg_globals.update(pkg_metadata)
    pkg_globals["__all__"] = list(pkg_metadata.keys())
