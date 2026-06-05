# GPT Image 2 PRD-grounded prompts: FoodMap / Local Food Journal Map

Use these only for PRD concept images. Do not present generated images as real product screenshots.

## Project basis

- Current status: V1.0 accepted; V1.2 recommendation layer implemented, 2026-06-04
- Product summary: 一张带照片、评分、回忆和扫街榜推荐层的本地私人美食地图。
- Key PRD boundary: V1.0/V1.2 不做账号、后端同步、多人协作、服务端照片存储、公网永久分享或公开榜单。 扫街榜当前数据不伪造 APP-only 条目，近似坐标需要收藏后手动校准。

## Experience concept

Wide 16:9 product presentation image based strictly on the PRD for FoodMap / Local Food Journal Map. Show the user-facing experience described here: 打开 #/map -> 搜索或地图点击新增 -> 填写评分/图层/笔记/照片 -> 按城市/标签/评分筛选 -> 加载扫街榜 -> 收藏推荐为个人记录 -> 生成只读快照或导入导出. Make it polished and rich, but avoid inventing features outside the listed PRD scope. No brand logos, no readable claims, no fake metrics.

## Capability / architecture concept

Wide 16:9 technical visual based strictly on the PRD/docs for FoodMap / Local Food Journal Map. Visualize these capabilities: V1.0 支持个人工作台、本地持久化、地图点位、图层管理、搜索筛选、照片、分享快照、导入导出。; V1.2 增加独立高德扫街榜推荐层、武汉推荐数据、推荐 marker、推荐面板和收藏为个人记录。; 推荐点与个人 FoodPlace 分层，保存后才进入用户正常数据模型。; 接入 AMap Open Platform key path，提高 POI 坐标精度。; 如果公共页面稳定，扩展更完整的扫街榜采集管线和推荐图例。; 账号、同步、协作、公网分享应作为 V2 后端范围另起。. Use abstract panels, evidence paths, source labels, and system boundaries. Do not imply forbidden capabilities.

## Future application concept

Wide 16:9 future scenario image based on the project's stated roadmap only: 个人旅行美食手账：城市旅行前后整理想去、已去、推荐和避雷地点。; 朋友分享：用只读快照和 .foodmap.json 传递本地地图包。; 轻量 POI 资料整理：不需要后端但需要地图管理的个人工具。. Clearly feel like a conceptual roadmap image, not an actual screenshot. No fake customer logos, no invented integrations, no readable product claims.
