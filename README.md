# BondVis

## Framework

Element UI, axios, iconfont, permission control, lint

## Requirements

Latest tested combination:  D3

Install [D3.js](https://d3js.org/)

Other required python libraries: numpy, pandas, tqdm etc.
## How to use it?

```bash
# clone the project
git clone https://github.com/WesleyClode/BondVis.git

# enter the project directory
cd BondVis

# install the front end dependencies
npm install
npm install --registry=https://registry.npm.taobao.org

# run the backend by typing in the command
# python run-data-backend.py(old)

# local mode
python run.py

# production mode
python run.py -prod
```

# run the frontend by typing in the command
npm run dev
```

This will automatically open http://localhost:9528

## Build

```bash
# build for test environment
npm run build:stage

# build for production environment
npm run build:prod
serve -s dist
```

## Advanced

```bash
# preview the release environment effect
npm run preview

# preview the release environment effect + static resource analysis
npm run preview -- --report

# code format check
npm run lint

# code format check and auto fix
npm run lint -- --fix
```

Refer to [Documentation](https://panjiachen.github.io/vue-element-admin-site/guide/essentials/deploy.html) for more information

## Backend package version
|Package Name | Version|
|----|----|
|flask|1.1.1|                
flask-cors          |      3.0.8                    
flask-pymongo       |      2.3.0       
gevent              |      1.4.0   
pandas              |      0.25.1  
pydash              |      4.8.0         
numpy               |      1.17.2   
pymongo             |      3.11.0         
chinese_calendar

## Demo

gif

## Related Project

This project is developed from 

## Browsers support

Modern browsers and Internet Explorer 10+.

| [<img src="https://raw.githubusercontent.com/alrra/browser-logos/master/src/edge/edge_48x48.png" alt="IE / Edge" width="24px" height="24px" />](http://godban.github.io/browsers-support-badges/)</br>IE / Edge | [<img src="https://raw.githubusercontent.com/alrra/browser-logos/master/src/firefox/firefox_48x48.png" alt="Firefox" width="24px" height="24px" />](http://godban.github.io/browsers-support-badges/)</br>Firefox | [<img src="https://raw.githubusercontent.com/alrra/browser-logos/master/src/chrome/chrome_48x48.png" alt="Chrome" width="24px" height="24px" />](http://godban.github.io/browsers-support-badges/)</br>Chrome | [<img src="https://raw.githubusercontent.com/alrra/browser-logos/master/src/safari/safari_48x48.png" alt="Safari" width="24px" height="24px" />](http://godban.github.io/browsers-support-badges/)</br>Safari |
| --------- | --------- | --------- | --------- |
| IE10, IE11, Edge| last 2 versions| last 2 versions| last 2 versions

## Packaging
前端打包步骤：
1. 将config.js的端口号改一下
2. 打包 
  tar -czvf BondVis_frontend_1203.tar.gz dist
3. 移动到服务器解压缩
  tar -xzvf BondVis_frontend_x.tar.gz

后端打包：
1. tar -czvf BondVis_backend_1129.tar.gz dist backend run.py config.py README.md
tar -czvf BondVis_backend_11.21.tar.gz backend run.py config.py README.md
2. split -b 39m BondVis2.3.tar.gz bondvis2.3_install/BondVis2.3.part-
3. cat BondVis_11.7.part-* > BondVis_11.7.tar.gz

# 在项目根目录下
1. 打包文件
首先，用 tar 命令打包文件：
tar -czvf BondVis2.1.tar.gz dist backend run.py config.py README.md
tar -czvf BondVis_frontend.11.12.tar.gz dist
tar -czvf BondVis_backend.11.211.tar.gz backend run.py config.py README.md
2. 拆分打包文件
使用 split 命令将打包后的文件拆分为多个不超过 39MB 的文件
split -b 39m BondVis2.0.tar.gz bondvis_install/BondVis2.0.part-
这将会在当前目录下生成以 BondVis2.0.part- 开头的多个文件，如 BondVis2.0.part-aa, BondVis2.0.part-ab 等等，每个文件大小不超过 39MB。

3. 合并拆分文件
首先使用 cat 命令将这些文件合并为一个：
cat BondVis2.0.part-* > BondVis2.0.tar.gz

4. 解压文件
tar -xzvf BondVis2.0.tar.gz
 
1726
1. 打包传输文件
# 创建一个目录来保存下载的包
mkdir packages

# 下载包及其依赖项
pip download networkx python-dateutil chinese_calendar scikit-learn -d packages

# 打包成一个压缩文件以便传输
tar -czvf packages.tar.gz packages


2.内网环境
# 解压缩文件
tar -xzvf packages.tar.gz

# 安装包
pip install --no-index --find-links=packages networkx python-dateutil chinese_calendar scikit-learn
