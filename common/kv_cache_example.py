#!/usr/bin/env python3
"""
KV缓存系统使用示例

这个文件展示了如何使用common/kv_cache.py和common/kv_sqlite.py模块
来实现高效的缓存系统。

运行前请安装依赖：
pip install aiosqlite

或使用uv:
uv add aiosqlite
"""

import asyncio
import time
from datetime import datetime
from typing import List, Optional

from common.kv_cache import create_cache_decorator
from common.kv_sqlite import SqliteKVDatabase, SqliteValueType


# 示例1: 基本KV存储操作
async def basic_kv_example():
    """基本KV存储操作示例"""
    print("🚀 基本KV存储操作示例")
    print("=" * 50)

    # 创建SQLite KV数据库
    db = SqliteKVDatabase(
        database_path="example.db",
        table_name="basic_cache",
        value_type=SqliteValueType.JSON,
    )

    try:
        # 存储不同类型的数据
        await db.put("string_key", "Hello, World!")
        await db.put("number_key", 42)
        await db.put("dict_key", {"name": "张三", "age": 30, "city": "北京"})
        await db.put("list_key", [1, 2, 3, "four", {"five": 5}])

        # 获取数据
        string_val = await db.get("string_key")
        number_val = await db.get("number_key")
        dict_val = await db.get("dict_key")
        list_val = await db.get("list_key")

        print(f"字符串值: {string_val}")
        print(f"数字值: {number_val}")
        print(f"字典值: {dict_val}")
        print(f"列表值: {list_val}")

        # 检查键是否存在
        exists = await db.has("string_key")
        print(f"键 'string_key' 存在: {exists}")

        not_exists = await db.has("non_existent_key")
        print(f"键 'non_existent_key' 存在: {not_exists}")

        # 获取所有键
        all_keys = await db.keys()
        print(f"所有键: {all_keys}")

        # 获取数据库统计
        count = await db.count()
        print(f"总记录数: {count}")

    finally:
        await db.close()

    print()


# 示例2: TTL（生存时间）功能
async def ttl_example():
    """TTL功能示例"""
    print("⏰ TTL（生存时间）功能示例")
    print("=" * 50)

    db = SqliteKVDatabase(
        database_path="ttl_example.db",
        table_name="ttl_cache",
        value_type=SqliteValueType.JSON,
    )

    try:
        # 存储数据
        await db.put(
            "temp_data",
            {"message": "这是临时数据", "timestamp": datetime.now().isoformat()},
        )

        # 立即获取（应该存在）
        data = await db.get("temp_data", ttl=5)  # 5秒TTL
        print(f"立即获取: {data}")

        # 等待3秒再获取（仍应存在）
        print("等待3秒...")
        await asyncio.sleep(3)
        data = await db.get("temp_data", ttl=5)
        print(f"3秒后获取: {data}")

        # 等待3秒再获取（应该已过期）
        print("再等待3秒...")
        await asyncio.sleep(3)
        data = await db.get("temp_data", ttl=5)
        print(f"6秒后获取: {data}")  # 应该返回None

    finally:
        await db.close()

    print()


# 示例3: 缓存装饰器使用
async def cache_decorator_example():
    """缓存装饰器使用示例"""
    print("🎯 缓存装饰器使用示例")
    print("=" * 50)

    # 创建数据库
    db = SqliteKVDatabase(
        database_path="decorator_cache.db",
        table_name="decorator_cache",
        value_type=SqliteValueType.JSON,
    )

    # 创建缓存装饰器
    cache = create_cache_decorator(db, default_ttl=10)  # 默认10秒缓存

    # 定义一些耗时的函数
    @cache(ttl=5, prefix="fibonacci")
    async def fibonacci(n: int) -> int:
        """计算斐波那契数列（带缓存）"""
        print(f"🧮 正在计算第 {n} 个斐波那契数...")
        if n <= 1:
            return n

        # 模拟耗时计算
        await asyncio.sleep(0.1)
        return await fibonacci(n - 1) + await fibonacci(n - 2)

    @cache(ttl=15, prefix="user_data")
    async def get_user_info(user_id: int) -> dict:
        """获取用户信息（带缓存）"""
        print(f"🔍 从数据库查询用户 {user_id} 的信息...")
        # 模拟数据库查询延迟
        await asyncio.sleep(0.5)

        return {
            "user_id": user_id,
            "name": f"用户{user_id}",
            "email": f"user{user_id}@example.com",
            "last_login": datetime.now().isoformat(),
        }

    try:
        # 测试斐波那契缓存
        print("测试斐波那契数列缓存:")
        start_time = time.time()
        result1 = await fibonacci(10)
        first_call_time = time.time() - start_time
        print(f"第一次调用 fibonacci(10) = {result1}, 耗时: {first_call_time:.3f}秒")

        start_time = time.time()
        result2 = await fibonacci(10)  # 应该从缓存获取
        second_call_time = time.time() - start_time
        print(f"第二次调用 fibonacci(10) = {result2}, 耗时: {second_call_time:.3f}秒")

        print(f"缓存加速比: {first_call_time / second_call_time:.1f}x")
        print()

        # 测试用户信息缓存
        print("测试用户信息缓存:")
        start_time = time.time()
        user1 = await get_user_info(123)
        first_call_time = time.time() - start_time
        print(f"第一次获取用户信息: {user1}")
        print(f"耗时: {first_call_time:.3f}秒")

        start_time = time.time()
        user2 = await get_user_info(123)  # 应该从缓存获取
        second_call_time = time.time() - start_time
        print(f"第二次获取用户信息: {user2}")
        print(f"耗时: {second_call_time:.3f}秒")

        print(f"缓存加速比: {first_call_time / second_call_time:.1f}x")

    finally:
        await db.close()

    print()


# 示例4: 批量操作
async def batch_operations_example():
    """批量操作示例"""
    print("📦 批量操作示例")
    print("=" * 50)

    db = SqliteKVDatabase(
        database_path="batch_example.db",
        table_name="batch_cache",
        value_type=SqliteValueType.JSON,
    )

    try:
        # 批量插入数据
        entries = [
            (f"user:{i}", {"id": i, "name": f"用户{i}", "score": i * 10})
            for i in range(1, 101)  # 100个用户
        ]

        print("批量插入100条用户记录...")
        start_time = time.time()
        await db.put_many(entries)
        insert_time = time.time() - start_time
        print(f"插入完成，耗时: {insert_time:.3f}秒")

        # 检查插入的数据
        count = await db.count()
        print(f"数据库中总记录数: {count}")

        # 获取前缀为 "user:" 的所有记录
        user_records = await db.get_with_prefix("user:", limit=10)
        print(f"前10个用户记录:")
        for record in user_records:
            print(f"  {record['key']}: {record['value']}")

        # 根据条件查找数据
        high_score_users = await db.find_by_condition(
            lambda data: isinstance(data, dict) and data.get("score", 0) > 500
        )
        print(f"分数大于500的用户数量: {len(high_score_users)}")

        # 批量删除一些数据
        keys_to_delete = [f"user:{i}" for i in range(90, 101)]  # 删除最后10个用户
        deleted_count = await db.delete_many(keys_to_delete)
        print(f"删除了 {deleted_count} 条记录")

        # 检查删除后的数量
        count_after_delete = await db.count()
        print(f"删除后的记录数: {count_after_delete}")

    finally:
        await db.close()

    print()


# 示例5: 不同数据类型
async def different_types_example():
    """不同数据类型示例"""
    print("🎨 不同数据类型示例")
    print("=" * 50)

    # 创建不同类型的数据库
    databases = {
        "JSON": SqliteKVDatabase("json_db.db", "json_store", SqliteValueType.JSON),
        "TEXT": SqliteKVDatabase("text_db.db", "text_store", SqliteValueType.TEXT),
        "INTEGER": SqliteKVDatabase("int_db.db", "int_store", SqliteValueType.INTEGER),
        "REAL": SqliteKVDatabase("real_db.db", "real_store", SqliteValueType.REAL),
        "BOOLEAN": SqliteKVDatabase(
            "bool_db.db", "bool_store", SqliteValueType.BOOLEAN
        ),
    }

    try:
        # JSON 类型
        json_db = databases["JSON"]
        await json_db.put(
            "complex_data",
            {
                "users": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}],
                "metadata": {"version": "1.0", "created": datetime.now().isoformat()},
            },
        )
        json_data = await json_db.get("complex_data")
        print(f"JSON数据: {json_data}")

        # TEXT 类型
        text_db = databases["TEXT"]
        await text_db.put("description", "这是一个文本描述，支持中文字符！")
        text_data = await text_db.get("description")
        print(f"TEXT数据: {text_data}")

        # INTEGER 类型
        int_db = databases["INTEGER"]
        await int_db.put("counter", 12345)
        int_data = await int_db.get("counter")
        print(f"INTEGER数据: {int_data} (类型: {type(int_data)})")

        # REAL 类型
        real_db = databases["REAL"]
        await real_db.put("pi", 3.14159265359)
        real_data = await real_db.get("pi")
        print(f"REAL数据: {real_data} (类型: {type(real_data)})")

        # BOOLEAN 类型
        bool_db = databases["BOOLEAN"]
        await bool_db.put("is_active", True)
        await bool_db.put("is_deleted", False)
        bool_data1 = await bool_db.get("is_active")
        bool_data2 = await bool_db.get("is_deleted")
        print(f"BOOLEAN数据: is_active={bool_data1} (类型: {type(bool_data1)})")
        print(f"BOOLEAN数据: is_deleted={bool_data2} (类型: {type(bool_data2)})")

        # 显示每个数据库的类型信息
        for name, db in databases.items():
            info = db.get_type_info()
            print(f"{name}数据库类型信息: {info}")

    finally:
        # 关闭所有数据库连接
        for db in databases.values():
            await db.close()

    print()


async def main():
    """主函数"""
    print("🎉 KV缓存系统示例程序")
    print("==" * 25)
    print()

    examples = [
        ("基本KV操作", basic_kv_example),
        ("TTL功能", ttl_example),
        ("缓存装饰器", cache_decorator_example),
        ("批量操作", batch_operations_example),
        ("不同数据类型", different_types_example),
    ]

    for name, example_func in examples:
        try:
            await example_func()
        except Exception as e:
            print(f"❌ 运行 {name} 示例时出错: {e}")
            print()

    print("✅ 所有示例运行完成！")
    print("\n💡 提示:")
    print("- 生成的数据库文件可以在当前目录找到")
    print("- 可以使用 SQLite 客户端查看数据库内容")
    print("- 在生产环境中建议配置数据库路径和适当的错误处理")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())
