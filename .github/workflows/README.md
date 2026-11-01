# 站一 SEO 自动化

两个 GitHub Actions workflow，全自动跑，不花一分钱（公开仓库 Actions 不计额度）。

## 1. SEO health check（每日 09:00 北京时间）

- 首页是否存活（200）
- robots.txt 是否存在、是否指向 sitemap
- sitemap.xml 能否解析、里面每个 URL 是否都返回 200
- 全站死链扫描（抓取每个页面的全部链接逐个检查，含外链）

失败会自动发邮件通知。有问题去仓库 **Actions** 标签页看当次运行的红字是哪一项。

## 2. IndexNow ping（有新页面/sitemap 更新时自动）

main 分支一旦推送了 `.html` 或 `sitemap.xml` 的变更，自动把 sitemap 里所有 URL 提交给 IndexNow，
通知 Bing、Yandex 等来抓取。Key 文件在仓库根目录 `<key>.txt`（IndexNow 要求公开可访问，属正常设计）。

**注意**：Google 不支持 IndexNow。新文章发布后，Google 收录仍需在 GSC 里手动"请求编入索引"（已在每篇文章的发布清单里）。

## 以后可以加的（需要 Daniel 动手）

- **GSC API 自动查收录/排名**：真正的"site: 收录了没""关键词排第几"只能走 Google Search Console API，
  需要 Daniel 在 Google Cloud 建 service account、加到 GSC 用户里，再把 key 存成仓库 secret。
  这一步涉及他的 Google 账号，得他亲手做，做完告诉我，我来接 workflow。
- 关键词排名监控：不建议爬 Google 搜索结果页（会被封）；正道是上面的 GSC API，或付费 SERP API。
