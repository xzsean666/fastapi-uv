"""
定义通用的KV存储接口和缓存装饰器
"""

import asyncio
import functools
import json
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional


class IKVDatabase(ABC):
    """通用的KV存储接口"""

    @abstractmethod
    async def get(self, key: str, ttl: Optional[int] = None) -> Optional[Any]:
        """获取值"""
        pass

    @abstractmethod
    async def put(self, key: str, value: Any) -> None:
        """存储值"""
        pass


def create_cache_decorator(db: IKVDatabase, default_ttl: int = 60):  # 默认60秒
    """创建缓存装饰器"""

    def cache(ttl: int = default_ttl, prefix: str = ""):
        """缓存装饰器

        Args:
            ttl: 缓存过期时间(秒)
            prefix: 缓存键前缀
        """

        def decorator(func: Callable):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    # 生成缓存键
                    args_str = json.dumps(args, default=str, ensure_ascii=False)
                    kwargs_str = json.dumps(
                        kwargs, default=str, ensure_ascii=False, sort_keys=True
                    )
                    cache_key = f"{prefix}:{func.__name__}:{args_str}:{kwargs_str}"

                    # 限制键长度
                    if len(cache_key) > 255:
                        cache_key = cache_key[:255]

                    # 使用通用的KV存储接口
                    cached = await db.get(cache_key, ttl)
                    if cached is not None:
                        return cached

                    # 执行原始方法
                    if asyncio.iscoroutinefunction(func):
                        result = await func(*args, **kwargs)
                    else:
                        result = func(*args, **kwargs)

                    # 存储结果到缓存
                    await db.put(cache_key, result)
                    return result

                except Exception:
                    # 如果缓存操作失败，直接执行原始方法
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)

            return wrapper

        return decorator

    return cache
