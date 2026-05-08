"""
密码哈希处理模块

使用 bcrypt 对密码进行哈希和验证
"""

from passlib.context import CryptContext

# 密码哈希上下文，使用 bcrypt 算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    对密码进行哈希

    Args:
        password: 明文密码

    Returns:
        哈希后的密码字符串
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码

    Args:
        plain_password: 明文密码
        hashed_password: 哈希后的密码

    Returns:
        验证通过返回 True，否则返回 False
    """
    return pwd_context.verify(plain_password, hashed_password)
