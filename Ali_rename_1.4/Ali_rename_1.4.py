# Ali-rename
# 仅供学习交流，请勿商用，若有不妥之处，侵联必删。
# Updated on April 20th  --by shadow-tiny

# 第一次使用需下载Aligo库 以及 TMDb库（请自行申请api）
# pip install --upgrade aligo
# pip install themoviedb

from aligo import Aligo
from themoviedb import TMDb
import re

def inf():
    while True:
        storage = int(input('你想更改的文件在：1:备份盘  2:资源盘\n'))

        if storage not in [1, 2]:
            print('输入错误，请重新输入！')
            continue

        # 设置drive_id为None，仅在选择资源盘时赋值
        drive_id = None
        if storage == 2:
            drives = ali.list_my_drives()
            drive_id = next((drive.drive_id for drive in drives if drive.drive_name == 'resource'), None)
            if not drive_id:
                print('资源盘未找到，请确保资源盘存在')
                continue

        # 循环获取有效的文件路径
        while True:
            path = input('请输入你想更改的文件的路径：')
            file = ali.get_folder_by_path(path, drive_id=drive_id)
            if file is None:
                print('指定的文件夹不存在，请重新输入！')
            else:
                break

        file_list = ali.get_file_list(file.file_id, drive_id=drive_id)
        print('----------获取信息完成----------')
        return file_list, path, drive_id


def scrape(file_list, path):
    # 获取唯一的文件后缀
    unique_suffixes = {file.name.split('.')[-1] for file in file_list}

    # 用户选择文件名中剧集标题的位置
    while True:
        choice = input('原文件名中剧集标题在哪两个符号之间：\n  1: [ 与 ] 之间\n  2: ] 与 [ 之间\n  3: ] 与 - 之间\n')
        pattern_choices = {
            '1': r"[\[\]]",  # 选择1和2都是方括号，但取不同的部分
            '2': r"[\[\]]",
            '3': r"[\]-]"
        }
        if choice in pattern_choices:
            parts = re.split(pattern_choices[choice], file_list[0].name)
            title = parts[1].strip() if choice in ['1', '2'] else parts[1].strip()
            print(title)
            break
        else:
            print("输入错误，请重新输入！")

    # 使用TMDb API查找剧集名称
    tmdb = TMDb(key="your API", language="zh-CN", region="CN") # key中可使用自己的API
    results = tmdb.search().multi(title)
    tv = [tmdb.tv(result.id).details() for result in results if result.is_tv()]

    # 处理查询结果
    if not tv:
        print("----------未查询到该剧集----------")
        tv_oname = None
    elif len(tv) == 1:
        tv_oname = tv[0].original_name
    else:
        print("选择你需要的剧集")
        for index, show in enumerate(tv, 1):
            print(f"    {index}: {show}")
        tv_oname = tv[int(input("请选择序号：")) - 1].original_name

    return list(unique_suffixes), tv_oname


# 批量重命名函数/集成后缀切割
def rename(file_list_2, name, suffixes, drive_id):
    # 输入重命名文件的季度
    ss = input('输入重命名文件的季度（位数<=2)：')
    # 初始化计数列表，其长度与后缀相同，全部元素设置为1
    ep = [1] * len(suffixes)
    # 创建新文件名列表
    new_name_list = []
    # 对每个文件进行处理
    for file in file_list_2:
        # 切割文件名以获取后缀
        suffix = file.name.split('.')[-1]
        # 特殊命名规则对于 .exe 文件
        if suffix == 'exe':
            new_name = f"{name}.{suffix}"
        else:
            # 找到后缀对应的索引
            if suffix in suffixes:
                index = suffixes.index(suffix)
                # 创建新文件名
                new_name = f"{name} S{ss.zfill(2)}E{ep[index]:03d}.{suffix}"
                # 更新计数器
                ep[index] += 1
        new_name_list.append(new_name)
    # 重命名文件
    for i in range(len(file_list_2)):
        try:
            new_file = ali.rename_file(file_list_2[i].file_id, new_name_list[i], drive_id=drive_id)
            print(f'已将{file_list_2[i].name}更改为{new_file.name}')
        except Exception as e:
            print(e)
            print(f'{file_list_2[i].name}更改失败')
    print('----------所有目标文件已更改完毕----------')
    return


if __name__ == '__main__':
    ali = Aligo()  #第一次使用会弹出二维码，可扫码登陆
    user = ali.get_user()  #获取用户信息
    [file_list, path, drive_id] = inf()
    file_list_2 = sorted(file_list, key=lambda x: x.name)  # 排序
    [suffixes, name] = scrape(file_list_2, path)  # 刮削剧集名称（附加文件后缀）
    rename(file_list_2, name, suffixes, drive_id)
