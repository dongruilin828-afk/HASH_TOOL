# =========================
# 应用信息
# =========================

APP_NAME = "Hash Tool"

APP_VERSION = "1.0.0"

APP_DESCRIPTION = "文本与文件哈希计算工具"

APP_AUTHOR = "Houlingderon"


# =========================
# Hash Tool 公共配置
# =========================


# GUI 中显示的算法名称
# 对应 hashlib 使用的名称
ALGORITHM_MAP = {
    "MD5": "md5",
    "SHA-1": "sha1",
    "SHA-256": "sha256",
    "SHA-512": "sha512",
}


# 各算法十六进制哈希值的正确长度
HASH_LENGTHS = {
    "MD5": 32,
    "SHA-1": 40,
    "SHA-256": 64,
    "SHA-512": 128,
}


# 默认算法
DEFAULT_ALGORITHM = "SHA-256"


# 文件分块读取大小
# 1024 * 1024 = 1 MB
FILE_CHUNK_SIZE = 1024 * 1024
