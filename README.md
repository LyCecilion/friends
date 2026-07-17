# CrystaRin 友链

本仓库通过 GitHub Issues 管理 [CrystaRin镜雨亭](https://crystal.stellalyr.ink/) 的友链数据，最终结果展示于 [友链页面](https://crystal.stellalyr.ink/social/)。

## 申请方式

1. 使用 [友链申请模板](https://github.com/LyCecilion/friends/issues/new/choose) 创建 Issue。
2. 填写站点标题、地址以及可选的图标、简介和订阅地址。
3. 等待零音人工审核；无需在申请前添加本站友链。
4. `审核中` 标签被移除后，友链会自动同步至展示页面。仓库所有者创建的申请会自动通过。

申请站点应当安全合规。请勿高频访问本站页面或订阅源。

没有 feed 的友链仍会正常展示，但可能排在已提供 feed 且近期更新的站点之后。站点信息发生变化时，可以直接编辑原 Issue。

## 本站信息

添加 CrystaRin 友链时，可以使用以下信息：

```yaml
title: CrystaRin镜雨亭
url: https://crystal.stellalyr.ink/
avatar: https://crystal.stellalyr.ink/assets/perlica_avatar.png
description: 我们不是理想的陈述者，而是理想的践行者。
feed: https://crystal.stellalyr.ink/atom.xml
```

## 数据同步

- Issue 创建或内容、标签、状态发生变化时，自动重新生成友链数据。
- 每天检查一次站点可达性，并更新失联状态。
- 每天解析一次订阅源，最多记录每个站点最新的 3 篇文章。
- 生成的数据位于 `output` 分支的 `v2/data.json`。

带有 `审核中` 或 `风险网站` 标签的 Issue 不会进入公开数据。只有仓库所有者可以通过移除 `审核中` 标签批准外部申请。
