"""KV缓存API示例 - 展示如何使用通用KV存储和缓存装饰器"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from app.config import settings
from app.dependencies import RateLimitDep, limiter
from common.kv_cache import create_cache_decorator
from common.kv_sqlite import SqliteKVDatabase, SqliteValueType

router = APIRouter(prefix=settings.api_prefix, tags=["kv-cache"])

# 初始化SQLite KV数据库
kv_db = SqliteKVDatabase(
    database_path="cache.db", table_name="cache_store", value_type=SqliteValueType.JSON
)

# 创建缓存装饰器
cache = create_cache_decorator(kv_db, default_ttl=300)  # 默认5分钟缓存


# Pydantic模型
class CacheItem(BaseModel):
    key: str
    value: Any
    ttl: Optional[int] = None


class CacheResponse(BaseModel):
    key: str
    value: Any
    success: bool
    message: str
    cached_at: Optional[str] = None


class UserData(BaseModel):
    user_id: int
    name: str
    email: str
    last_login: str


class MessageResponse(BaseModel):
    message: str
    data: Any = None


# 模拟业务服务类
class UserService:
    """用户服务类 - 演示缓存使用"""

    def __init__(self):
        # 模拟用户数据
        self._users = {
            1: {"name": "张三", "email": "zhangsan@example.com"},
            2: {"name": "李四", "email": "lisi@example.com"},
            3: {"name": "王五", "email": "wangwu@example.com"},
        }

    @cache(ttl=600, prefix="user")  # 10分钟缓存
    async def get_user_by_id(self, user_id: int) -> Optional[UserData]:
        """获取用户信息（带缓存）"""
        print(f"🔍 从数据库查询用户 {user_id}...")  # 只有缓存失效时才会执行

        # 模拟数据库查询延迟
        await asyncio.sleep(0.5)

        if user_id not in self._users:
            return None

        user_data = self._users[user_id]
        return UserData(
            user_id=user_id,
            name=user_data["name"],
            email=user_data["email"],
            last_login=datetime.now().isoformat(),
        )

    @cache(ttl=1800, prefix="user_list")  # 30分钟缓存
    async def get_all_users(self) -> List[UserData]:
        """获取所有用户（带缓存）"""
        print("🔍 从数据库查询所有用户...")

        # 模拟数据库查询延迟
        await asyncio.sleep(1.0)

        return [
            UserData(
                user_id=uid,
                name=data["name"],
                email=data["email"],
                last_login=datetime.now().isoformat(),
            )
            for uid, data in self._users.items()
        ]

    async def expensive_calculation(self, number: int) -> Dict[str, Any]:
        """耗时计算（不使用缓存装饰器，手动缓存）"""
        cache_key = f"calc:{number}"

        # 尝试从缓存获取
        cached_result = await kv_db.get(cache_key, ttl=120)  # 2分钟缓存
        if cached_result is not None:
            print(f"💾 从缓存获取计算结果: {number}")
            return cached_result

        print(f"🧮 执行复杂计算: {number}")
        # 模拟复杂计算
        await asyncio.sleep(2.0)

        result = {
            "input": number,
            "square": number**2,
            "factorial": 1,
            "computed_at": datetime.now().isoformat(),
        }

        # 计算阶乘
        factorial = 1
        for i in range(1, min(number + 1, 21)):  # 限制到20以避免数字过大
            factorial *= i
        result["factorial"] = factorial

        # 存储到缓存
        await kv_db.put(cache_key, result)

        return result


# 初始化服务
user_service = UserService()


# API端点
@router.get(
    "/user/{user_id}",
    response_model=MessageResponse,
    summary="获取用户信息",
    description="获取指定用户信息，使用缓存加速响应",
)
@limiter.limit(f"{settings.rate_limit_requests}/minute")
async def get_user(request: Request, user_id: int, _: RateLimitDep):
    """获取用户信息（带缓存）"""
    try:
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        return MessageResponse(message="用户信息获取成功", data=user.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/users",
    response_model=MessageResponse,
    summary="获取所有用户",
    description="获取所有用户列表，使用缓存加速响应",
)
@limiter.limit(f"{settings.rate_limit_requests}/minute")
async def get_users(request: Request, _: RateLimitDep):
    """获取所有用户（带缓存）"""
    try:
        users = await user_service.get_all_users()
        return MessageResponse(
            message="用户列表获取成功", data=[user.model_dump() for user in users]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/calculate/{number}",
    response_model=MessageResponse,
    summary="复杂计算",
    description="执行复杂计算，使用手动缓存优化",
)
@limiter.limit(f"{settings.rate_limit_requests}/minute")
async def calculate(request: Request, number: int, _: RateLimitDep):
    """复杂计算（手动缓存）"""
    if number < 0 or number > 100:
        raise HTTPException(status_code=400, detail="数字必须在0-100之间")

    try:
        result = await user_service.expensive_calculation(number)
        return MessageResponse(message="计算完成", data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/cache",
    response_model=CacheResponse,
    status_code=status.HTTP_201_CREATED,
    summary="设置缓存",
    description="手动设置缓存键值对",
)
@limiter.limit(f"{settings.rate_limit_requests}/minute")
async def set_cache(request: Request, item: CacheItem, _: RateLimitDep):
    """设置缓存"""
    try:
        await kv_db.put(item.key, item.value)

        return CacheResponse(
            key=item.key,
            value=item.value,
            success=True,
            message="缓存设置成功",
            cached_at=datetime.now().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/cache/{key}",
    response_model=CacheResponse,
    summary="获取缓存",
    description="根据键获取缓存值",
)
@limiter.limit(f"{settings.rate_limit_requests}/minute")
async def get_cache(
    request: Request, key: str, _: RateLimitDep, ttl: Optional[int] = None
):
    """获取缓存"""
    try:
        value = await kv_db.get(key, ttl=ttl, include_timestamps=True)

        if value is None:
            raise HTTPException(status_code=404, detail="缓存键不存在或已过期")

        if isinstance(value, dict) and "value" in value:
            # 包含时间戳的情况
            return CacheResponse(
                key=key,
                value=value["value"],
                success=True,
                message="缓存获取成功",
                cached_at=value.get("created_at"),
            )
        else:
            # 只有值的情况
            return CacheResponse(
                key=key, value=value, success=True, message="缓存获取成功"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/cache/{key}",
    response_model=MessageResponse,
    summary="删除缓存",
    description="删除指定的缓存键",
)
@limiter.limit(f"{settings.rate_limit_requests}/minute")
async def delete_cache(request: Request, key: str, _: RateLimitDep):
    """删除缓存"""
    try:
        deleted = await kv_db.delete(key)

        if not deleted:
            raise HTTPException(status_code=404, detail="缓存键不存在")

        return MessageResponse(message="缓存删除成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/cache-stats",
    response_model=MessageResponse,
    summary="缓存统计",
    description="获取缓存数据库统计信息",
)
@limiter.limit(f"{settings.rate_limit_requests}/minute")
async def get_cache_stats(request: Request, _: RateLimitDep):
    """获取缓存统计"""
    try:
        total_count = await kv_db.count()
        all_keys = await kv_db.keys()

        # 按前缀分类统计
        prefix_stats = {}
        for key in all_keys:
            prefix = key.split(":")[0] if ":" in key else "unknown"
            prefix_stats[prefix] = prefix_stats.get(prefix, 0) + 1

        return MessageResponse(
            message="缓存统计获取成功",
            data={
                "total_entries": total_count,
                "prefix_stats": prefix_stats,
                "database_info": kv_db.get_type_info(),
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/cache/clear",
    response_model=MessageResponse,
    summary="清空缓存",
    description="清空所有缓存数据",
)
@limiter.limit("5/minute")  # 更严格的限制
async def clear_cache(request: Request, _: RateLimitDep):
    """清空所有缓存"""
    try:
        await kv_db.clear()
        return MessageResponse(message="缓存已清空")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
