# 优先从locales模块导入，并执行方法i18n，进行docstrigns的国际化，避免先import的模块的docstrings没有正确国际化
from .locales import *

i18n()
try:
    from .jupyter import *
    from .viz import *
    from ._version import version_info, __version__
    from .rest import *
    from .portal import *
    from .online import *
    from .server import Server
    from ipyleaflet import *


    def _jupyter_nbextension_paths():
        return [{
            'section': 'notebook',
            'src': 'static',
            'dest': 'iclientpy',
            'require': 'iclientpy/extension'
        }]
except ModuleNotFoundError as err:
    import inspect
    stacks = inspect.stack()
    stack = stacks[len(stacks) - 1]
    filename = stack.filename
    if 'iclient' in filename and 'rest' in filename and 'cmd' in filename:
        pass
    else:
        raise err