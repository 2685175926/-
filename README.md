# 章鱼监控在线版

这是把原来的 `章鱼监控.html + proxy.py` 整理后的单体部署项目：

- `/` 打开监控页面
- `/api/...` 转发到 `https://ad.adintl.cn/...`
- 页面里的默认 Base URL 已改成 `/api`

## 本地运行

```bash
pip install -r requirements.txt
python app.py
```

打开：

```text
http://127.0.0.1:8899/
```

## 部署到 Render

1. 把本目录上传到一个 GitHub 仓库。
2. 打开 Render，选择 `New` -> `Web Service`。
3. 连接这个 GitHub 仓库。
4. Build Command 填：

```bash
pip install -r requirements.txt
```

5. Start Command 填：

```bash
gunicorn app:app
```

6. 部署完成后打开 Render 给你的域名，例如：

```text
https://你的项目名.onrender.com/
```

建议在 Render 的 `Environment` 里添加两个环境变量，给网站加访问密码：

```text
SITE_USERNAME=你的用户名
SITE_PASSWORD=你的密码
```

## 注意

页面里的 `X-Access-Token` 仍然由你手动输入，不会写死在后端代码里。这个站点包含代理接口和自动停止投放功能，线上地址不要公开分享。建议一定设置上面的 `SITE_USERNAME` 和 `SITE_PASSWORD`。
