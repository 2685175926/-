# 上线操作单

推荐部署方式：GitHub + Render。

## 1. 上传到 GitHub

1. 打开 https://github.com/new
2. Repository name 填：`octopus-monitor-site`
3. 选择 `Private`，不要公开。
4. 点 `Create repository`。
5. 按 GitHub 页面提示，把本目录代码推送上去。

如果你想用命令行推送，在本目录执行：

```bash
git init
git add .
git commit -m "Deploy octopus monitor"
git branch -M main
git remote add origin 你的GitHub仓库地址
git push -u origin main
```

## 2. Render 创建网站

1. 打开 https://dashboard.render.com/
2. 点 `New +` -> `Web Service`
3. 连接刚才的 GitHub 仓库。
4. Runtime 选择 `Python`。
5. Build Command 填：

```bash
pip install -r requirements.txt
```

6. Start Command 填：

```bash
gunicorn app:app
```

7. Environment Variables 添加：

```text
SITE_USERNAME=你自己设置的用户名
SITE_PASSWORD=你自己设置的密码
```

8. 点 `Deploy Web Service`。

## 3. 使用

部署完成后打开 Render 给你的域名，例如：

```text
https://octopus-monitor-site.onrender.com/
```

浏览器会先弹出网站登录框，输入 `SITE_USERNAME` 和 `SITE_PASSWORD`。进入页面后，在 `X-Access-Token` 输入框里粘贴 token，Base URL 保持 `/api`。

## 安全提醒

这个网站有广告数据读取和停止投放能力。仓库建议设为 Private，Render 网站一定设置 `SITE_USERNAME` 和 `SITE_PASSWORD`。

## 虚拟主机部署

只有支持 Python Web 应用的虚拟主机才能部署本项目。后台通常会有类似 `Setup Python App`、`Python Selector`、`Passenger`、`WSGI` 的功能。

如果虚拟主机只支持上传 `html/php`，不能运行 Python 常驻 Web 服务，就不能部署这个项目，因为 `/api` 代理必须由 Python 后端处理。

常见 cPanel Python App 步骤：

1. 进入 cPanel，打开 `Setup Python App`。
2. Python 版本选择 `3.10`、`3.11` 或 `3.12`。
3. Application root 指向项目目录，例如：`octopus-monitor-site`。
4. Application URL 选择你的域名或子目录。
5. Application startup file 填：`passenger_wsgi.py`。
6. Application Entry point 填：`application`。
7. 进入虚拟环境后安装依赖：

```bash
pip install -r requirements.txt
```

8. 设置环境变量：

```text
SITE_USERNAME=你自己设置的用户名
SITE_PASSWORD=你自己设置的密码
```

9. 点击 Restart/Reload App。

如果后台没有环境变量设置入口，可以先不设置 `SITE_USERNAME` 和 `SITE_PASSWORD` 测试页面是否能打开，但正式使用不建议裸奔。
