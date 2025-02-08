#!/bin/bash

# 启动 React 应用
npm run dev &

# 切换到 server 文件夹并启动 Python 应用
# python app.py &

# 启动另一个 Python 进程
python run-data-backend.py &


# chmod +x start.sh

# start
# ./start.sh
