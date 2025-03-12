from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.models.database import HistoryItemModel

router = APIRouter(prefix="/api/history", tags=["history"])

# 模拟内存存储，在实际应用中应该使用数据库
history_items: List[HistoryItemModel] = []
next_id = 1

@router.get("/", response_model=List[HistoryItemModel])
async def get_history_items():
    """获取查询历史记录"""
    return history_items

@router.post("/", response_model=HistoryItemModel)
async def add_history_item(item: HistoryItemModel):
    """添加历史记录项"""
    global next_id
    
    # 如果没有ID，则分配一个
    if not item.id:
        item.id = next_id
        next_id += 1
    
    # 确保时间戳存在
    if not item.timestamp:
        item.timestamp = datetime.now()
    
    history_items.append(item)
    return item

@router.delete("/{item_id}")
async def delete_history_item(item_id: int):
    """删除历史记录项"""
    global history_items
    
    original_length = len(history_items)
    history_items = [item for item in history_items if item.id != item_id]
    
    if len(history_items) == original_length:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"找不到ID为{item_id}的历史记录"
        )
    
    return {"message": f"已删除ID为{item_id}的历史记录"}

@router.delete("/")
async def clear_history():
    """清空所有历史记录"""
    global history_items
    history_items = []
    return {"message": "已清空所有历史记录"}