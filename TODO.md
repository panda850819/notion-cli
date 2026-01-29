# TODO - notion-cli

## P1 - 應該修復

### 1. [formatters.py:21] 型別問題 - `get_title` 可能回傳 None

```python
# 問題：item.get("name") 可能是 None
if item.get("name"):
    return item.get("name")  # 這裡可能回傳 None
```

**修復方式**：
```python
name = item.get("name")
if name:
    return name
```

### 2. [task.py:22,45] 硬編碼 property name "Name"

不同 database 的 title 欄位名稱可能不同（如 "Task", "Title", "任務名稱"）。

**修復方式**：
- 偵測 database schema 中哪個 property 是 title 類型
- 或讓使用者指定 `--title-property` 參數

### 3. [db.py:32] limit 只在 client 端截斷

```python
rows = client.query_database(database_id)
format_database_rows(rows[:limit], db_schema)  # 浪費 API 資源
```

**修復方式**：將 limit 傳給 API（`page_size` 參數）

---

## P2 - 建議修復

### 4. [client.py] 缺少 pagination 支援

Notion API 預設只返回 100 筆。需要處理 `has_more` 和 `next_cursor`。

### 5. [client.py:36] 型別推斷問題

```python
params = {"query": query}  # dict[str, str]
params["filter"] = {...}   # 變成 dict[str, str | dict]
```

**修復方式**：使用 `dict[str, Any]` 或分開處理

### 6. 缺少測試

加入基本的 unit tests（pytest）。
