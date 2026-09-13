import sys
import os
from loguru import logger
import time
import api_halo
from pathlib import Path
from dotenv import load_dotenv

# 移除 loguru 默认的 handler
logger.remove(0)

# 控制台输出
logger.add(
    sys.stdout,
    format='[{time:YYYY-MM-DD HH:mm:ss}] [{level}] {message}',
    level='INFO',
    colorize=True
)

# 文件输出
logger.add(
    './logs/run_{time:YYYY-MM-DD}.log',
    format='[{time:YYYY-MM-DD HH:mm:ss}] [{level}] {message}',
    level='INFO',
    rotation='1 days',
    retention=90,
    encoding='utf-8'
)


def main():
    logger.info('=' * 60)
    load_dotenv()
    logger.info('请求发起备份……')
    retention_time = api_halo.new_dt(os.getenv('RETENTION_TIME', '259200'))
    domain = os.getenv('DOMAIN')
    token = os.getenv('PERSONAL_TOKEN')
    save_location = Path(os.getenv('SAVE_LOCATION', '.'))
    auto_down = os.getenv('AUTO_DOWN', 'true')
    del_bak = os.getenv('DEL_BAK', 'true')

    if not domain or not token:
        logger.error('配置缺失：请在 .env 文件中设置 DOMAIN 和 PERSONAL_TOKEN')
        return

    bak_r = api_halo.create_bak(domain, retention_time, token)
    if bak_r[1] == 201:
        logger.info('请求发起备份成功')
        while True:
            status_all = api_halo.check_status(domain, token)
            status = status_all[0]
            filename = status_all[1]
            name = status_all[2]
            if status == 'SUCCEEDED':
                logger.info(f'成功完成备份，文件名: {filename}')
                break
            elif status == 'RUNNING':
                logger.info('等待halo完成备份……')
                time.sleep(3)
    else:
        logger.error(f'出现错误，响应代码: {bak_r[1]} 响应文本: {bak_r[0]}')
        return

    if auto_down.lower() == 'true':
        logger.info('准备下载备份文件……')
        save_path = save_location / filename  # 自动加分隔符，兼容所有平台
        r = api_halo.down_bak(domain, name, filename, token, str(save_path))
        logger.info(f'下载完成，文件已保存在: {r}')
        if del_bak == 'true':
            logger.info('请求删除备份……')
            del_bak_r = api_halo.del_bak(domain, name, token)
            if del_bak_r == 'OK':
                logger.info('删除备份成功')
            else:
                logger.error(f'出现错误，响应代码: {del_bak_r[1]} 响应文本: {del_bak_r[0]}')


if __name__ == '__main__':
    main()
