import os
import sys
import xbmc
import xbmcaddon
from shutil import *

ADDON = xbmcaddon.Addon('script.skin.stream-cinema')
SKIN = xbmcaddon.Addon(xbmc.getSkinDir())
KODI_VERSION = int(xbmc.getInfoLabel("System.BuildVersion").split(".")[0])


def log(message, level=xbmc.LOGNOTICE):
    xbmc.log("[BBaron]: %s" % (str(message)), level=level)


def copy():
    src = xbmc.translatePath(SKIN.getAddonInfo("path") + '/resources/stream-cinema')
    dest = xbmc.translatePath('special://userdata/library/video/stream-cinema')
    log("remove dest dir")
    try:
        rmtree(dest)
    except:
        pass
    copytree(src, dest)


def get_setting(setting):
    return ADDON.getSetting(setting).strip().decode('utf-8')


def set_setting(setting, value):
    ADDON.setSetting(setting, str(value))


def get_setting_as_bool(setting):
    return get_setting(setting).lower() == "true"


def get_setting_as_float(setting):
    try:
        return float(get_setting(setting))
    except ValueError:
        return 0


def get_setting_as_int(setting):
    try:
        return int(get_setting_as_float(setting))
    except ValueError:
        return 0


def Sget_setting(setting):
    return xbmc.getInfoLabel("Skin.HasSetting(%s)" % setting).decode("utf-8")


def Sset_setting(setting, value):
    xbmc.executebuiltin("Skin.SetBool(%s,%s)" % (setting.encode("utf-8"), value.encode("utf-8")))


def Sget_setting_as_bool(setting):
    return Sget_setting(setting).lower() == "true"


def copytree(src, dst, symlinks=False, ignore=None):
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()
    if not os.path.isdir(dst):
        os.makedirs(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            log("copy {0} to {1}".format(srcname, dstname))
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                copy2(srcname, dstname)
        except Error as err:
            errors.extend(err.args[0])
        except EnvironmentError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        errors.extend((src, dst, str(why)))
    if errors:
        raise Error(errors)


def sleep(sleep_time):
    while not xbmc.abortRequested and sleep_time > 0:
        sleep_time -= 100
        xbmc.sleep(99)


def getCondVisibility(text):
    if KODI_VERSION < 17:
        text = text.replace("Integer.IsGreater", "IntegerGreaterThan")
        text = text.replace("String.Contains", "SubString")
        text = text.replace("String.IsEqual", "StringCompare")
    return xbmc.getCondVisibility(text)


def checkSkinPath():
    SKIN = xbmcaddon.Addon(xbmc.getSkinDir())
    sdir = xbmc.translatePath(SKIN.getAddonInfo("path") + '/resources/stream-cinema')
    if os.path.isdir(sdir):
        log("skin %s ma podporu pre stream-cinema" % xbmc.getSkinDir())
        return True
    log("skin %s nema podporu pre stream-cinema" % xbmc.getSkinDir())
    sleep(10000)
    return False


def startup():
    xbmc.startServer(xbmc.SERVER_WEBSERVER, True)
    xbmc.startServer(xbmc.SERVER_JSONRPCSERVER, True)
    while not xbmc.abortRequested and not checkSkinPath():
        sleep(1000)
        pass


if __name__ == "__main__":
    startup()

    if not xbmc.abortRequested:
        action = None
        if len(sys.argv) > 1:
            action = sys.argv[1]

        log('first_run: %s' % str(get_setting_as_bool('first_run')))
        if get_setting_as_bool('first_run') is not True or action == 'update':
            log('first_run/update')
            try:
                copy()
                set_setting('first_run', 'true')
                if action != 'update':
                    Sset_setting('SCMainMenuWidget', 'true')
                    Sset_setting('SCMain', 'true')
                    Sset_setting('HomeMenuNoStreamCinemaButton', 'false')
                xbmc.executebuiltin("ReloadSkin()")
            except Exception as e:
                log('error copy files')
                pass
        else:
            log('do nothing: {0}/{1}'.format(str(action), str(get_setting_as_bool('first_run'))))
    log("exit service")
