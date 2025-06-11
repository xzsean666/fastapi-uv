"""
SQLite KV存储数据库实现
"""

import json
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import aiosqlite

from .kv_cache import IKVDatabase


class SqliteValueType(Enum):
    """支持的数据类型枚举"""

    JSON = "json"  # 存储为text，序列化JSON
    TEXT = "text"  # 纯文本
    BLOB = "blob"  # 二进制数据
    INTEGER = "integer"  # 整数
    REAL = "real"  # 浮点数
    BOOLEAN = "boolean"  # 布尔值（存储为integer）


class TypeHandler(ABC):
    """类型处理器接口"""

    @abstractmethod
    def serialize(self, value: Any) -> Any:
        """序列化值"""
        pass

    @abstractmethod
    def deserialize(self, value: Any) -> Any:
        """反序列化值"""
        pass

    @property
    @abstractmethod
    def column_type(self) -> str:
        """列类型"""
        pass


class JSONTypeHandler(TypeHandler):
    """JSON类型处理器"""

    def serialize(self, value: Any) -> str:
        return json.dumps(value, default=self._bigint_handler, ensure_ascii=False)

    def deserialize(self, value: Any) -> Any:
        return json.loads(value)

    @property
    def column_type(self) -> str:
        return "TEXT"

    def _bigint_handler(self, obj):
        """处理大整数"""
        if isinstance(obj, int) and abs(obj) > 2**53:
            return str(obj)
        return obj


class TextTypeHandler(TypeHandler):
    """文本类型处理器"""

    def serialize(self, value: Any) -> str:
        return str(value)

    def deserialize(self, value: Any) -> str:
        return value

    @property
    def column_type(self) -> str:
        return "TEXT"


class BlobTypeHandler(TypeHandler):
    """二进制类型处理器"""

    def serialize(self, value: Any) -> bytes:
        if isinstance(value, bytes):
            return value
        elif isinstance(value, (bytearray, memoryview)):
            return bytes(value)
        elif isinstance(value, str):
            return value.encode("utf-8")
        else:
            raise ValueError(
                "BLOB type requires bytes, bytearray, memoryview, or string"
            )

    def deserialize(self, value: Any) -> bytes:
        return value

    @property
    def column_type(self) -> str:
        return "BLOB"


class IntegerTypeHandler(TypeHandler):
    """整数类型处理器"""

    def serialize(self, value: Any) -> int:
        num = int(value)
        return num

    def deserialize(self, value: Any) -> int:
        return int(value)

    @property
    def column_type(self) -> str:
        return "INTEGER"


class RealTypeHandler(TypeHandler):
    """浮点数类型处理器"""

    def serialize(self, value: Any) -> float:
        return float(value)

    def deserialize(self, value: Any) -> float:
        return float(value)

    @property
    def column_type(self) -> str:
        return "REAL"


class BooleanTypeHandler(TypeHandler):
    """布尔值类型处理器"""

    def serialize(self, value: Any) -> int:
        return 1 if value else 0

    def deserialize(self, value: Any) -> bool:
        return bool(value)

    @property
    def column_type(self) -> str:
        return "INTEGER"


# 类型处理器映射
TYPE_HANDLERS: Dict[SqliteValueType, TypeHandler] = {
    SqliteValueType.JSON: JSONTypeHandler(),
    SqliteValueType.TEXT: TextTypeHandler(),
    SqliteValueType.BLOB: BlobTypeHandler(),
    SqliteValueType.INTEGER: IntegerTypeHandler(),
    SqliteValueType.REAL: RealTypeHandler(),
    SqliteValueType.BOOLEAN: BooleanTypeHandler(),
}


class SqliteKVDatabase(IKVDatabase):
    """SQLite KV存储数据库"""

    def __init__(
        self,
        database_path: Optional[str] = None,
        table_name: str = "kv_store",
        value_type: SqliteValueType = SqliteValueType.JSON,
    ):
        self.database_path = database_path or ":memory:"
        self.table_name = table_name
        self.value_type = value_type
        self.type_handler = TYPE_HANDLERS[value_type]
        self.initialized = False
        self._connection = None

    async def _ensure_initialized(self) -> None:
        """确保数据库已初始化"""
        if not self.initialized:
            self._connection = await aiosqlite.connect(self.database_path)

            # 创建表
            await self._connection.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    key TEXT PRIMARY KEY,
                    value {self.type_handler.column_type},
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # 创建更新时间戳的触发器
            await self._connection.execute(
                f"""
                CREATE TRIGGER IF NOT EXISTS update_{self.table_name}_timestamp
                AFTER UPDATE ON {self.table_name}
                BEGIN
                    UPDATE {self.table_name} SET updated_at = CURRENT_TIMESTAMP WHERE key = NEW.key;
                END
            """
            )

            await self._connection.commit()
            self.initialized = True

    async def put(self, key: str, value: Any) -> None:
        """存储键值对"""
        await self._ensure_initialized()

        serialized_value = self.type_handler.serialize(value)
        await self._connection.execute(
            f"INSERT OR REPLACE INTO {self.table_name} (key, value) VALUES (?, ?)",
            (key, serialized_value),
        )
        await self._connection.commit()

    async def get(
        self, key: str, ttl: Optional[int] = None, include_timestamps: bool = False
    ) -> Optional[Any]:
        """获取值"""
        await self._ensure_initialized()

        cursor = await self._connection.execute(
            f"SELECT value, created_at, updated_at FROM {self.table_name} WHERE key = ?",
            (key,),
        )
        row = await cursor.fetchone()

        if not row:
            return None

        value, created_at, updated_at = row

        # 检查是否过期
        if ttl is not None:
            created_time = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            current_time = datetime.now()
            if (current_time - created_time).total_seconds() > ttl:
                await self.delete(key)
                return None

        deserialized_value = self.type_handler.deserialize(value)

        if include_timestamps:
            return {
                "value": deserialized_value,
                "created_at": created_at,
                "updated_at": updated_at,
            }

        return deserialized_value

    async def delete(self, key: str) -> bool:
        """删除键值对"""
        await self._ensure_initialized()

        cursor = await self._connection.execute(
            f"DELETE FROM {self.table_name} WHERE key = ?", (key,)
        )
        await self._connection.commit()
        return cursor.rowcount > 0

    async def add(self, key: str, value: Any) -> None:
        """添加键值对（键不存在时）"""
        await self._ensure_initialized()

        # 检查键是否已存在
        if await self.has(key):
            raise ValueError(f'Key "{key}" already exists')

        await self.put(key, value)

    async def close(self) -> None:
        """关闭数据库连接"""
        if self._connection:
            await self._connection.close()
            self.initialized = False

    async def get_all(self) -> Dict[str, Any]:
        """获取所有键值对"""
        await self._ensure_initialized()

        cursor = await self._connection.execute(
            f"SELECT key, value FROM {self.table_name}"
        )
        rows = await cursor.fetchall()

        return {key: self.type_handler.deserialize(value) for key, value in rows}

    async def get_many(self, limit: int = 10) -> Dict[str, Any]:
        """获取限定数量的键值对"""
        await self._ensure_initialized()

        cursor = await self._connection.execute(
            f"SELECT key, value FROM {self.table_name} LIMIT ?", (limit,)
        )
        rows = await cursor.fetchall()

        return {key: self.type_handler.deserialize(value) for key, value in rows}

    async def keys(self) -> List[str]:
        """获取所有键"""
        await self._ensure_initialized()

        cursor = await self._connection.execute(f"SELECT key FROM {self.table_name}")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]

    async def has(self, key: str) -> bool:
        """检查键是否存在"""
        await self._ensure_initialized()

        cursor = await self._connection.execute(
            f"SELECT 1 FROM {self.table_name} WHERE key = ? LIMIT 1", (key,)
        )
        row = await cursor.fetchone()
        return row is not None

    async def put_many(
        self, entries: List[Tuple[str, Any]], batch_size: int = 1000
    ) -> None:
        """批量添加键值对"""
        await self._ensure_initialized()

        # 分批处理大量数据
        for i in range(0, len(entries), batch_size):
            batch = entries[i : i + batch_size]

            # 序列化批次数据
            serialized_batch = [
                (key, self.type_handler.serialize(value)) for key, value in batch
            ]

            await self._connection.executemany(
                f"INSERT OR REPLACE INTO {self.table_name} (key, value) VALUES (?, ?)",
                serialized_batch,
            )
            await self._connection.commit()

    async def delete_many(self, keys: List[str]) -> int:
        """批量删除键"""
        await self._ensure_initialized()

        if not keys:
            return 0

        placeholders = ",".join("?" * len(keys))
        cursor = await self._connection.execute(
            f"DELETE FROM {self.table_name} WHERE key IN ({placeholders})", keys
        )
        await self._connection.commit()
        return cursor.rowcount

    async def clear(self) -> None:
        """清空数据库"""
        await self._ensure_initialized()

        await self._connection.execute(f"DELETE FROM {self.table_name}")
        await self._connection.commit()

    async def count(self) -> int:
        """获取记录数量"""
        await self._ensure_initialized()

        cursor = await self._connection.execute(
            f"SELECT COUNT(*) FROM {self.table_name}"
        )
        row = await cursor.fetchone()
        return row[0] if row else 0

    async def find_by_value(self, value: Any, exact: bool = True) -> List[str]:
        """根据值查找键"""
        await self._ensure_initialized()

        serialized_value = self.type_handler.serialize(value)

        if exact:
            cursor = await self._connection.execute(
                f"SELECT key FROM {self.table_name} WHERE value = ?",
                (serialized_value,),
            )
        else:
            # 模糊搜索（仅适用于文本类型）
            if self.value_type not in [SqliteValueType.TEXT, SqliteValueType.JSON]:
                raise ValueError(
                    f"Fuzzy search not supported for {self.value_type.value} type"
                )

            cursor = await self._connection.execute(
                f"SELECT key FROM {self.table_name} WHERE value LIKE ?",
                (f"%{serialized_value}%",),
            )

        rows = await cursor.fetchall()
        return [row[0] for row in rows]

    async def find_by_condition(
        self, condition: Callable[[Any], bool]
    ) -> Dict[str, Any]:
        """根据条件查找值"""
        await self._ensure_initialized()

        cursor = await self._connection.execute(
            f"SELECT key, value FROM {self.table_name}"
        )
        rows = await cursor.fetchall()

        matched_records = {}
        for key, value in rows:
            deserialized_value = self.type_handler.deserialize(value)
            if condition(deserialized_value):
                matched_records[key] = deserialized_value

        return matched_records

    def get_value_type(self) -> SqliteValueType:
        """获取当前使用的值类型"""
        return self.value_type

    def get_type_info(self) -> Dict[str, str]:
        """获取类型处理器信息"""
        return {
            "value_type": self.value_type.value,
            "column_type": self.type_handler.column_type,
        }

    async def get_with_prefix(
        self,
        prefix: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: str = "ASC",
        include_timestamps: bool = False,
    ) -> List[Dict[str, Any]]:
        """高效获取指定前缀的所有键值对"""
        await self._ensure_initialized()

        if not prefix:
            raise ValueError("Prefix cannot be empty")

        # 构建查询
        select_fields = ["key", "value"]
        if include_timestamps:
            select_fields.extend(["created_at", "updated_at"])

        query = f"""
            SELECT {', '.join(select_fields)}
            FROM {self.table_name}
            WHERE key >= ? AND key < ?
            ORDER BY key {order_by}
        """

        params = [prefix, prefix + "\xff"]  # 使用 \xFF 作为范围上限

        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)

        if offset is not None:
            query += " OFFSET ?"
            params.append(offset)

        cursor = await self._connection.execute(query, params)
        rows = await cursor.fetchall()

        results = []
        for row in rows:
            result = {"key": row[0], "value": self.type_handler.deserialize(row[1])}

            if include_timestamps:
                result["created_at"] = row[2]
                result["updated_at"] = row[3]

            results.append(result)

        return results
