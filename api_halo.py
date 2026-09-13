import json
import os
from datetime import datetime, timezone, timedelta

import requests
from tqdm import tqdm


# 计算备份保留时间
def new_dt(seconds):
    now_utc = datetime.now(timezone.utc)
    dt_new = now_utc + timedelta(seconds=int(seconds))
    iso_str = dt_new.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    return iso_str


# 创建备份的函数
def create_bak(domain, time, token):
    r = requests.post(url=f'{domain}/apis/migration.halo.run/v1alpha1/backups',
                      data='''
                        {
                            "apiVersion": "migration.halo.run/v1alpha1",
                            "kind": "Backup",
                            "metadata": {
                                "generateName": "backup-",
                                "name": ""
                            },
                            "spec": {
                                "expiresAt": "%s"
                            }
                        }
                      ''' % time,
                      headers={'content-type': 'application/json', 'Authorization': f'Bearer {token}'}, timeout=10)
    code = r.status_code
    return [r.text, code]


# 检查备份创建是否完成
def check_status(domain, token):
    r = requests.get(url=f'{domain}/apis/migration.halo.run/v1alpha1/backups',
                     headers={'Authorization': f'Bearer {token}'}, timeout=10)
    data = json.loads(r.text)
    status = data['items'][0]['status']['phase']
    try:
        filename = data['items'][0]['status']['filename']
        name = data['items'][0]['metadata']['name']
    except KeyError:
        filename = ''
        name = ''
    return [status, filename, name]


# 下载备份
def down_bak(domain, name, filename, token, save_path):
    # 发起请求，启用流式传输
    response = requests.get(
        f'{domain}/apis/console.api.migration.halo.run/v1alpha1/backups/{name}/files/{filename}',
        headers={'Authorization': f'Bearer {token}'},
        stream=True)
    response.raise_for_status()  # 检查请求是否成功

    # 获取文件总大小（字节），可能为 None
    total_size = int(response.headers.get('content-length', 0))

    # 确保保存目录存在
    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)

    # 使用 tqdm 显示进度条
    with open(save_path, 'wb') as file, tqdm(
            desc=os.path.basename(save_path),
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:  # 过滤掉 keep-alive 的空块
                file.write(chunk)
                bar.update(len(chunk))

    return save_path


# 删除备份
def del_bak(domain, name, token):
    r = requests.delete(url=f'{domain}/apis/migration.halo.run/v1alpha1/backups/{name}',
                        headers={'Authorization': f'Bearer {token}'}, timeout=10)
    if r.status_code == 200:
        return 'OK'
    else:
        return [r.text, r.status_code]
