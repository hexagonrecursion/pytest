import warnings
from pathlib import Path
from typing import Optional

from ..compat import LEGACY_PATH
from ..deprecated import HOOK_LEGACY_PATH_ARG
from _pytest.nodes import _imply_path

# hookname: (Path, LEGACY_PATH)
imply_paths_hooks = {
    "pytest_ignore_collect": ("fspath", "path"),
    "pytest_collect_file": ("fspath", "path"),
    "pytest_pycollect_makemodule": ("fspath", "path"),
    "pytest_report_header": ("startpath", "startdir"),
    "pytest_report_collectionfinish": ("startpath", "startdir"),
}


class PathAwareHookProxy:
    def __init__(self, hook_caller):
        self.__hook_caller = hook_caller

    def __dir__(self):
        return dir(self.__hook_caller)

    def __getattr__(self, key):
        if key not in imply_paths_hooks:
            return getattr(self.__hook_caller, key)
        else:
            hook = getattr(self.__hook_caller, key)
            path_var, fspath_var = imply_paths_hooks[key]

            def fixed_hook(**kw):
                path_value: Optional[Path] = kw.pop(path_var, None)
                fspath_value: Optional[LEGACY_PATH] = kw.pop(fspath_var, None)
                if fspath_value is not None:
                    warnings.warn(
                        HOOK_LEGACY_PATH_ARG.format(
                            pylib_path_arg=fspath_var, pathlib_path_arg=path_var
                        )
                    )
                path_value, fspath_value = _imply_path(path_value, fspath_value)
                kw[path_var] = path_value
                kw[fspath_var] = fspath_value
                return hook(**kw)

            fixed_hook.__name__ = key
            return fixed_hook
