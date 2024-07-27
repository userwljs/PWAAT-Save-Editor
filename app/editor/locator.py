import os
import winreg
from logging import getLogger
from typing import Any

from .installed_apps import find_desktop_app, find_universal_app, App

logger = getLogger(__name__)


def _read_reg(ep, p = r"", k = ''):
    try:
        key = winreg.OpenKeyEx(ep, p)
        value = winreg.QueryValueEx(key,k)
        if key:
            winreg.CloseKey(key)
        return value[0]
    except Exception as e:
        return None

STEAM_SAVE_LENGTH = 1496880
XBOX_SAVE_LENGTH = 1492008
XBOX_APP_NAME = 'F024294D.PhoenixWrightAceAttorneyTrilogy_8fty0by30jkny'
STEAM_APP_NAME = 'Steam App 787480'
class _Locator:
    
    def __init__(self) -> None:
        self.__xbox_app_cache: App | None = None
    
    def __xbox_app(self) -> App | None:
        return find_universal_app(XBOX_APP_NAME)
    
    @property
    def system_steam_save_path(self) -> list[str]:
        """
        默认 Steam 存档路径。
        """
        steam_path = self.steam_path
        if not steam_path:
            logger.warning('Steam not found')
            return []
        saves_path = os.path.join(steam_path, 'userdata')
        # 列出子文件夹（多账号）
        accounts = os.listdir(saves_path)
        save_files = []
        for account in accounts:
            save_file = os.path.join(saves_path, account, '787480', 'remote', 'systemdata')
            if os.path.exists(save_file):
                assert os.path.getsize(save_file) == STEAM_SAVE_LENGTH
                save_files.append(save_file)
        return save_files
    
    @property
    def system_xbox_save_path(self) -> list[str]:
        """
        默认 Xbox 存档路径。
        """
        appdata_local = os.environ.get('LOCALAPPDATA')
        if not appdata_local:
            logger.error('%LOCALAPPDATA% not found')
            return []
        save_folder = os.path.join(appdata_local, 'Packages', XBOX_APP_NAME, 'SystemAppData', 'wgs')
        # 列出所有文件，寻找大小为 XBOX_SAVE_LENGTH 的文件
        save_files = []
        for root, _, files in os.walk(save_folder):
            for file in files:
                path = os.path.join(root, file)
                if os.path.getsize(path) == XBOX_SAVE_LENGTH:
                    save_files.append(path)
        return save_files
        
    @property
    def steam_path(self) -> str | None:
        """
        Steam 安装路径（steam.exe）。
        """
        path32 = _read_reg(ep = winreg.HKEY_LOCAL_MACHINE, p = r"SOFTWARE\Wow6432Node\Valve\Steam", k = 'InstallPath')
        path64 = _read_reg(ep = winreg.HKEY_LOCAL_MACHINE, p = r"SOFTWARE\Valve\Steam", k = 'InstallPath')
        return path32 or path64
    
    @property
    def steam_game_path(self) -> str | None:
        """
        Steam 游戏安装路径。
        """
        app = find_desktop_app(STEAM_APP_NAME)
        return app.installed_path if app else None
    
    @property
    def xbox_game_path(self) -> str | None:
        """
        Xbox 游戏安装路径。
        """
        app = self.__xbox_app()
        return app.installed_path if app else None

_ins = _Locator()


system_steam_save_path = _ins.system_steam_save_path
system_xbox_save_path = _ins.system_xbox_save_path
steam_path = _ins.steam_path
steam_game_path = _ins.steam_game_path
xbox_game_path = _ins.xbox_game_path


if __name__ == '__main__':
    print(_ins.steam_path)
    print(_ins.steam_game_path)
    print(_ins.xbox_game_path)
    print(_ins.system_xbox_save_path)
    print(_ins.system_steam_save_path)