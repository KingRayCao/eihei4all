# Eihei4All

图片投稿 / 展示 / 轮播网站。Everyone can be an EiHeiChan!

全程采用AI开发，用时约2h。AI大人太强大了。

## 板块说明

| 路由 | 功能 |
|------|------|
| `/upload` | 登录后投稿、查看所有投稿、管理自己的图片 |
| `/gallery` | 浏览P图，鼠标悬浮显示导航与筛选 |
| `/carousel` | 自动轮播P图，参数写入URL可供OBS直接使用 |
| `/admin` | 管理员后台（用户审批、权限管理、删除记录） |

## Carousel URL 参数

```
/carousel?days=7&interval=5&info=true
```

| 参数 | 含义 | 默认值 |
|------|------|--------|
| `days` | 筛选最近N天的投稿，0=全部 | `7` |
| `interval` | 轮播间隔秒数 | `5` |
| `info` | 是否显示作者/标题 | `true` |

## 部署（Docker Compose）

1. 修改 `docker-compose.yml` 中的 `SECRET_KEY` 和 `SUPER_ADMIN_PASSWORD`
2. 运行：

```bash
docker compose up -d --build
```

3. 访问 `http://your-server-ip`，使用 `admin` 账号进入后台审批用户

## 本地开发

**后端：**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**前端：**
```bash
cd frontend
npm install
npm run dev
```

前端开发服务器会自动代理 `/api` 和 `/uploads` 到 `localhost:8000`。

## 支持的图片格式

`.jpg` `.jpeg` `.png` `.gif` `.webp` `.bmp`（GIF 在轮播中会循环播放）
