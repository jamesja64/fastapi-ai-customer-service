#!/bin/bash

echo "🧹 檢查並清理嵌套的 pycharm_v1 目錄..."

# 檢查是否存在嵌套目錄
if [ -d "pycharm_v1/pycharm_v1" ]; then
    echo "❌ 發現嵌套目錄: pycharm_v1/pycharm_v1"
    
    # 移動文件到正確位置
    if [ -d "pycharm_v1/pycharm_v1/fastapi-ai-customer-service" ]; then
        echo "📁 移動文件到正確位置..."
        find pycharm_v1/pycharm_v1/fastapi-ai-customer-service -type f -exec cp {} pycharm_v1/fastapi-ai-customer-service/ \;
    fi
    
    # 刪除嵌套目錄
    echo "🗑️  刪除嵌套目錄..."
    rm -rf pycharm_v1/pycharm_v1
    
    echo "✅ 嵌套目錄已清理完成"
else
    echo "✅ 目錄結構正確，無需清理"
fi

echo "📂 當前目錄結構："
ls -la pycharm_v1/ | head -10
