import os
import time
import random
import subprocess
import sys
import logging

# 配置多账号环境变量前缀
ACCOUNT_PREFIX = "98ACCOUNT_"
# 间隔时间范围(秒)
MIN_INTERVAL = 600
MAX_INTERVAL = 1200
# 自定义回复的环境变量名
AUTO_REPLIES_ENV = "AUTO_REPLIES"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger()

def get_custom_replies():
    """从环境变量获取自定义回复内容"""
    replies_text = os.getenv(AUTO_REPLIES_ENV, '')
    if not replies_text:
        logger.info("未设置自定义回复，将使用默认回复")
        return None
    
    # 按行分割，过滤空行
    replies = [line.strip() for line in replies_text.split('\n') if line.strip()]
    if not replies:
        logger.info("自定义回复为空，将使用默认回复")
        return None
    
    logger.info(f"已加载 {len(replies)} 条自定义回复")
    return replies

def main():
    # 从系统环境变量获取
    account_envs = {}
    for key, value in os.environ.items():
        if key.startswith(ACCOUNT_PREFIX):
            account_num = key.replace(ACCOUNT_PREFIX, "")
            account_envs[account_num] = value
    
    if not account_envs:
        logger.warning("未找到多账号配置，格式应为 98ACCOUNT_1, 98ACCOUNT_2, ...")
        return
    
    logger.info(f"找到 {len(account_envs)} 个账号配置")
    
    # 获取自定义回复
    custom_replies = get_custom_replies()
    
    # 使用相对路径查找daysign.py (与multi_daysign.py在同一目录)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    daysign_path = os.path.join(script_dir, "daysign.py")
    
    if not os.path.exists(daysign_path):
        logger.error(f"无法找到daysign.py文件，请确保它与multi_daysign.py在同一目录")
        return
    
    logger.info(f"使用的daysign.py路径: {daysign_path}")
    
    # 依次处理每个账号
    for idx, (account_num, account_value) in enumerate(account_envs.items()):
        logger.info(f"\n处理账号 {account_num} 中...")
        
        # 设置临时环境变量
        env = os.environ.copy()
        env["FETCH_98TANG"] = account_value
        
        # 如果有自定义回复，随机选择一条
        if custom_replies:
            random_reply = random.choice(custom_replies)
            env["CUSTOM_REPLY"] = random_reply
            logger.info(f"已为此次执行选择回复: {random_reply}")
        
        # 调用daysign.py
        try:
            result = subprocess.run(
                [sys.executable, daysign_path], 
                env=env, 
                check=True,
                capture_output=True,
                text=True
            )
            logger.info(f"账号 {account_num} 执行结果:")
            logger.info(result.stdout)
            
            if result.stderr:
                logger.error(f"错误信息: {result.stderr}")
        except subprocess.CalledProcessError as e:
            logger.error(f"账号 {account_num} 执行失败: {e}")
            logger.error(f"错误输出: {e.stderr}")
        
        # 如果不是最后一个账号，则等待随机时间
        if idx < len(account_envs) - 1:
            wait_time = random.randint(MIN_INTERVAL, MAX_INTERVAL)
            logger.info(f"等待 {wait_time} 秒后处理下一个账号...")
            time.sleep(wait_time)
    
    logger.info("\n所有账号处理完成!")

if __name__ == "__main__":
    main() 