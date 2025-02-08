#!/bin/bash

# 定义需要查找的端口号
ports=("9528" "5003")

# 遍历每个端口号
for port in "${ports[@]}"; do
  # 使用 lsof 和 grep 查找占用指定端口号的 PID
  pids=$(lsof -ti :$port)
  
  # 检查是否找到了 PID
  if [ -n "$pids" ]; then
    # 使用 kill 命令终止进程
    kill -9 $pids
    echo "Processes with PIDs $pids for port $port killed."
  else
    echo "No processes found for port $port."
  fi
done
