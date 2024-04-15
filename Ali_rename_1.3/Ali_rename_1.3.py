# 1.3版本实现tv剧集的自动挂削原产国名称，为infuse挂削原数据提高正确率
# 需要用户在阿里云上创建正确剧集译名的文件夹
# 可以支持文件夹中最多三种的格式（eg. nfo/ass/mkv or mp4）同时进行批量重命名
# 仅供学习交流，请勿商用，若有不妥之处，侵联必删。
# Updated on April 15th  --by wsubset

# 第一次使用需下载Aligo库 以及 TMDb库（请自行申请api）
# pip install --upgrade aligo
# pip install themoviedb



# 获取阿里云用户信息
def inf():
    path = input('请输入你想更改的文件的路径（备份盘）：')
    file = ali.get_folder_by_path(path)
    if file is None:
        raise RuntimeError('指定的文件夹不存在')
    file_list = ali.get_file_list(file.file_id)
    print('----------获取信息完成----------')
    return file_list,path

# file_list 排序函数
def file_sort(file_list):
    # 可查看未排序前的 id-name 映射
    # file_list
    # 新增一个int list并与原list排序相同
    j = 0
    num_list = []
    for file in file_list:
        num = ''.join(re.findall(r'\d',file_list[j].name))
        num_list.append(num)
        j += 1
    # 合并并排序两条list
    folder_list = list(zip(num_list,file_list))
    folder_list = sorted(folder_list,key = (lambda x:x[0]))
    # 合并后切片保留id-name
    folder_list_2 = [row[1] for row in folder_list]
    return folder_list_2

# 刮削path最底层目录名称函数（附加文件后缀）/来源非原文件名称
def scrape(file_list,path):
    # 正则切割出两个文件后缀（假设仅存在视频格式与字幕格式）（最多支持三种后缀）
    suffix = []
    ra_str_1 = re.split('\.',file_list[0].name)
    suffix_1 = ra_str_1[-1]
    ra_str_2 = re.split('\.',file_list[1].name)
    suffix_2 = ra_str_2[-1]
    ra_str_3 = re.split('\.',file_list[2].name)
    suffix_3 = ra_str_3[-1]
    # 切割文件名并匹配原产国名称
    n_match = path.split('/')[-1]
    tv_oname = None #带出局部变量
    tmdb = TMDb(key="YOUR API KEY", language="zh-CN", region="CN")  #在此处修改为自己的api，可根据需求修改语言地区参数
    results = tmdb.search().multi(n_match)
    for result in results:
        if result.is_tv():
            tv = tmdb.tv(result.id).details()
            tv_oname = tv.original_name
#            print(tv, tv.original_name)
        else:
            continue
    if tv_oname is None:
        print("----------未查询到该剧集----------")
    # else在完成后可以注释掉
#    else:
#        print(tv_oname)
    return suffix_1,suffix_2,suffix_3,tv_oname

# 批量重命名函数/集成后缀切割
def rename(folder_list_2,file_list,name,suffix_1,suffix_2):
    # 创建新文件名列表
    ss = input('输入季度<=2位：')
    new_name_list = []
    ep1 = ep2 = ep3 = 1
    p = 0
    for file in file_list:
        # 切割对应文件后缀
        ra_str = re.split('\.',folder_list_2[p].name)
        suffix = ra_str[-1]
        # 新文件名创建
        if suffix_1 == suffix:
            new_name = name + ' S' + str(ss).rjust(2,'0') + 'E' + str(ep1).rjust(2,'0') + '.' + suffix
            new_name_list.append(new_name)
            ep1 += 1
        elif suffix_2 == suffix:
            new_name = name + ' S' + str(ss).rjust(2,'0') + 'E' + str(ep2).rjust(2,'0') + '.' + suffix
            new_name_list.append(new_name)
            ep2 += 1
        else:
            new_name = name + ' S' + str(ss).rjust(2,'0') + 'E' + str(ep3).rjust(2,'0') + '.' + suffix
            new_name_list.append(new_name)
            ep3 += 1
        p += 1
    # 逐个更改，防止数据错位不可发现
    p = 0
    for file in file_list:
        try:
            new_file = ali.rename_file(folder_list_2[p].file_id,new_name_list[p])
            print('已将{}更改为{}'.format(folder_list_2[p].name,new_file.name))
            p += 1
        except Exception as e:
            print(e)
            print('{}更改失败'.format(folder_list_2[p].name))
    print('----------所有目标文件已更改完毕----------')
    return

from aligo import Aligo
from themoviedb import TMDb
import re


if __name__ == '__main__':
    ali = Aligo() #第一次使用会弹出二维码，可扫码登陆
    user = ali.get_user() #获取用户信息
    [file_list,path] = inf()
    # 调用排序函数
    folder_list_2 = file_sort(file_list)
    [suffix_1,suffix_2,suffix_3,name] = scrape(folder_list_2,path)
    rename(folder_list_2,file_list,name,suffix_1,suffix_2)