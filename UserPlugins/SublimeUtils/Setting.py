import copy
import functools as ft
from collections import defaultdict
import dpath.util
import sublime
from ..MUtils import Os
from . import WView

_extendVariableTokens = {
    "!lower": lambda v: v.lower(),
    "!upper": lambda v: v.upper(),
}

@WView.fwPrepareWindow
def expandVariables(window, *strs, forSublime=True, forEnv=True):
    sublimeVariables = window.extract_variables()
    extendVariables = {}
    for token, processFn in _extendVariableTokens.items():
        extendVariables.update({
            k+token: processFn(v)
            for k, v in sublimeVariables.items()
            if isinstance(v, str)
        })

    sublimeVariables.update(extendVariables)


    retStrs = [sublime.expand_variables(s, sublimeVariables)
               for s in strs] if forSublime else strs
    retStrs = Os.expandVariables(*retStrs) if forEnv else retStrs

    return retStrs


class PluginSetting(object):
    def __init__(self, key, ext='sublime-settings'):
        self.key = key
        self.settingFileName = ".".join([key, ext])
        self.defOpts = None
        self.settings = None
        self.opts = None
        self.dynOpts = None
        self.prevOpts = defaultdict(lambda: None)

    def load(self):
        self.settings = sublime.load_settings(self.settingFileName)
        return self

    def loadWithDefault(self, defOpts, *, onChanged=None, target=None):
        self.load()
        self.defOpts = copy.deepcopy(defOpts)
        self.opts = self.getSetting(target, **self.defOpts)
        self.updateDynOpts()
        def _onChanged():
            nowOpts = self.getSetting(target, **self.defOpts)
            if nowOpts == self.opts:
                return

            self.prevOpts = self.opts
            self.opts = nowOpts
            if onChanged is not None:
                onChanged()

        self.settings.add_on_change(self.key, _onChanged)
        if onChanged is not None:
            onChanged()

    def onPluginUnload(self):
        self.clear_on_change()

    def updateDynOpts(self, **dynKwds):
        self.dynOpts = {k: dynKwds.get(k, v) for k, v in self.opts.items()}

    def isValid(self):
        return self.settings is not None

    def clear_on_change(self):
        if self.isValid():
            self.settings.clear_on_change(self.key)

    def __getattr__(self, name):
        try:
            return getattr(self.settings, name)
        except KeyError:
            raise AttributeError

    def forTarget(self, target, defVal=None, reLoad=False):
        if reLoad:
            self.load()

        if defVal is None:
            setting = self.settings.get(target)
        else:
            setting = self.settings.get(target, defVal)

        return ft.partial(dpath.util.values, setting)

    def getSetting(self, target=None, expandVarialbe=True, **defaultSettings):
        settings = {}
        if target is None:
            for k, defVal in defaultSettings.items():
                val = self.get(k, defVal)
                if expandVarialbe and isinstance(val, str):
                    settings[k], = expandVariables(None, val)
                else:
                    settings[k] = val
        else:
            _getSetting = self.forTarget(target, {})
            for k, defVal in defaultSettings.items():
                [val] = _getSetting(k) or [defVal]
                if expandVarialbe and isinstance(val, str):
                    settings[k], = expandVariables(None, val)
                else:
                    settings[k] = val

        return settings





