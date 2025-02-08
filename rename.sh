#!/bin/bash

# 遍历匹配 BondVis2.0part-*.zip 的文件
for file in BondVis2.0part-*.zip; do
  # 提取文件名的基部（不包括 .zip 扩展名）
  base=${file%.zip}
  # 新的文件名将是 BondVis2.0.part-aa
  new_name="${base/BondVis2.0part-/BondVis2.0.part-}"
  # 重命名文件
  mv "$file" "$new_name"
done
