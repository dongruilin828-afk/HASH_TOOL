import hashlib

from config import FILE_CHUNK_SIZE


def calculate_hash(
    text: str,
    algorithm: str = "sha256"
) -> str:
    """
    计算字符串的哈希值。

    参数：
        text:
            要计算哈希的字符串。

        algorithm:
            hashlib 使用的算法名称，
            例如 md5、sha1、sha256、sha512。

    返回：
        十六进制格式的哈希字符串。
    """

    # 将 Python 字符串编码为 UTF-8 字节
    data = text.encode("utf-8")

    # 创建对应的哈希对象
    hash_object = hashlib.new(algorithm)

    # 加入数据
    hash_object.update(data)

    # 返回十六进制哈希
    return hash_object.hexdigest()


def calculate_file_hash(
    file_path: str,
    algorithm: str = "sha256",
    chunk_size: int = FILE_CHUNK_SIZE
) -> str:
    """
    计算文件的哈希值。

    使用分块读取，
    避免一次性把大型文件全部读取到内存。

    参数：
        file_path:
            文件路径。

        algorithm:
            hashlib 使用的算法名称。

        chunk_size:
            每次读取的字节数量。
            默认 1 MB。

    返回：
        十六进制格式的文件哈希值。
    """

    with open(file_path, "rb") as file:
        return calculate_stream_hash(
            file,
            algorithm,
            chunk_size
        )


def calculate_stream_hash(
    stream,
    algorithm: str = "sha256",
    chunk_size: int = FILE_CHUNK_SIZE
) -> str:
    """计算已打开的二进制流的哈希值。"""

    hash_object = hashlib.new(algorithm)

    for chunk in iter(
        lambda: stream.read(chunk_size),
        b""
    ):
        hash_object.update(chunk)

    return hash_object.hexdigest()
