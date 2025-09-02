import os
import sys
import subprocess
import shlex
from pathlib import Path


def get_valid_choice(prompt, valid_choices):
    while True:
        choice = input(prompt).strip().lower()
        if choice in valid_choices:
            return choice
        print(f"无效输入，请从 {valid_choices} 中选择")


def get_file_path(prompt, filetype=None):
    while True:
        path = input(prompt).strip()
        if not path:
            continue

        expanded_path = os.path.abspath(os.path.expanduser(path))
        if os.path.isfile(expanded_path):
            if not filetype or expanded_path.lower().endswith(filetype):
                return expanded_path
            print(f"文件类型错误，请提供{filetype}文件")
        else:
            print("文件不存在，请重新输入")


def get_icon_path():
    while True:
        path = input("图标文件路径 (可选，直接回车跳过): ").strip()
        if not path:
            return None

        expanded_path = os.path.abspath(os.path.expanduser(path))
        if os.path.isfile(expanded_path):
            if expanded_path.lower().endswith('.ico'):
                return expanded_path
            print("图标必须是.ico格式文件")
        else:
            print("文件不存在，请重新输入")


def find_pyinstaller():
    """尝试定位PyInstaller可执行文件"""
    # 尝试直接调用pyinstaller
    try:
        subprocess.run(["pyinstaller", "--version"],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        return "pyinstaller"
    except (FileNotFoundError, OSError):
        pass

    # 尝试使用python -m PyInstaller
    try:
        subprocess.run([sys.executable, "-m", "PyInstaller", "--version"],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        return [sys.executable, "-m", "PyInstaller"]
    except (FileNotFoundError, OSError):
        pass

    # 尝试在Python脚本目录中查找
    script_path = os.path.join(sys.prefix, "Scripts", "pyinstaller.exe")
    if os.path.isfile(script_path):
        return script_path

    # 尝试在虚拟环境目录中查找
    if hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix:
        venv_script_path = os.path.join(sys.prefix, "Scripts", "pyinstaller.exe")
        if os.path.isfile(venv_script_path):
            return venv_script_path

    return None


def main():
    print("=" * 50)
    print("PyInstaller 打包工具")
    print("=" * 50)

    # 定位PyInstaller
    pyinstaller_cmd = find_pyinstaller()
    if not pyinstaller_cmd:
        print("❌ 无法找到PyInstaller，请确保已正确安装")
        print("提示: 尝试使用 'pip install pyinstaller' 安装")
        return

    # 获取要转换的.py文件路径
    py_file = get_file_path("\n请输入要转换的.py文件路径: ", filetype='.py')
    file_name = Path(py_file).stem

    # 获取打包选项
    onefile = get_valid_choice("打包为单文件? (y/n): ", ['y', 'n']) == 'y'
    console = get_valid_choice("显示控制台窗口? (y/n): ", ['y', 'n']) == 'y'
    icon_path = get_icon_path()

    # 获取高级选项
    print("\n高级选项 (空格分隔，直接回车跳过):")
    print("可用选项: --add-data, --hidden-import, --noconfirm, --log-level等")
    raw_advanced = input("> ").strip()

    # 构建命令
    if isinstance(pyinstaller_cmd, list):
        cmd = pyinstaller_cmd.copy()
    else:
        cmd = [pyinstaller_cmd]

    cmd.append('--clean')
    if onefile:
        cmd.append('--onefile')
    if not console:
        cmd.append('--noconsole')
    if icon_path:
        cmd.append(f'--icon={icon_path}')
    if raw_advanced:
        try:
            cmd.extend(shlex.split(raw_advanced))
        except ValueError:
            print("高级选项格式错误，将被忽略")

    cmd.append(py_file)

    # 确认执行
    print("\n" + "=" * 50)
    print("即将执行命令:")
    print(' '.join(cmd))
    print("=" * 50)

    if get_valid_choice("\n确认执行? (y/n): ", ['y', 'n']) == 'y':
        try:
            # 使用当前工作目录作为工作目录
            subprocess.run(cmd, check=True, cwd=os.getcwd())
            print(f"\n✅ 成功生成可执行文件! 输出目录: {os.path.abspath('dist')}")
        except subprocess.CalledProcessError as e:
            print(f"\n❌ 打包失败! 错误代码: {e.returncode}")
        except Exception as e:
            print(f"\n❌ 发生意外错误: {type(e).__name__} - {str(e)}")
    else:
        print("\n操作已取消")


if __name__ == "__main__":
    main()