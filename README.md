# TreasureHunts

寻宝游戏要求：

- 每个游戏玩家都有一定数量的金币、宝物。有一个市场供玩家们买卖宝物。玩家可以将宝物放到市场上挂牌，自己确定价格。其他玩家支付足够的金币，可购买宝物。
- 宝物分为两类：一类为工具，它决定持有玩家的工作能力；一类为配饰，它决定持有玩家的运气。
- 每位玩家每天可以通过寻宝获得一件宝物，宝物的价值由玩家的运气决定。每位玩家每天可以通过劳动赚取金币，赚得多少由玩家的工作能力决定。（游戏中的一天可以是现实中的1分钟、5分钟、10分钟，自主设定。）
- 每个宝物都有一个自己的名字（尽量不重复）。每位玩家能够佩戴的宝物是有限的（比如一个玩家只能佩戴一个工具和两个配饰）。多余的宝物被放在存储箱中，不起作用，但可以拿到市场出售。
- 在市场上挂牌的宝物必须在存储箱中并仍然在存储箱中，直到宝物被卖出。挂牌的宝物可以被收回，并以新的价格重新挂牌。当存储箱装不下时，运气或工作能力值最低的宝物将被系统自动回收。
- 假设游戏永不停止而玩家的最终目的是获得最好的宝物。

要求完成以下操作

寻宝（可以自动每天一次）、赚钱（可以自动每天一次）、佩戴宝物、浏览市场、买宝物、挂牌宝物、收回宝物

使用前端demo进行开发，在开发中对前端页面进行了一些修改

## 数据库设计

显然我们需要有一个 `Collection` 用来存储用户信息，这里我们设计此 `User Collection` 如下：

```json
{
  "username": "virgil",
  "pwd": "e10adc3949ba59abbe56e057f20f883e",
  "money": 10,
  "luck": 0,
  "work": 0,
  "backpack": [],
  "arm": []
}
```

条目解释：

- `username` 用户名
- `pwd` 用户密码 (经过 `md5` 哈希后的)
- `money` 用户拥有的金钱
- `luck` 幸运值, 由装备的配饰决定
- `work` 工作能力, 由装备的工具决定
- `backpack` 背包(存储箱), 最大存储量为 `20`
- `arm` 装备栏, 最大装备数为 `3`

> 这里 `backpack` 与 `arm` 都是数组, 存储着装备的编号

那么由于我们在上面设计了 `backpack` 这种数组形式的存储, 所以我们需要对装备也同样设置一个 `Collection`名为 `Treasure` , 具体而言: 

```json
{
  "treasureId": 2,
  "name": "充电器",
  "class": 0,
  "property": 10,
  "quality": 10,
  "level": "等级一"
}
```

条目解释:

- `treasureId` 装备编号
- `name` 装备名称
- `class` 装备类别, 其中 0 为工具类, 1为配饰类
- `property` 装备的属性, 对工具类来说这是工作能力, 对配饰类来说这是幸运值
- `quality` 装备的质量, 关系到自动淘汰机制
- `level` 装备的品级

但是这样还不够, 因为我们需要满足玩家之间可以通过市场交互这一机制, 所以我们对市场也建立一个 `Collection` 名为 `Market` 进行管理, 具体而言:

```json
{
  "treasureId": 1,
  "price": 10,
  "seller": "virgil"
}
```

对于市场内的每个条目, 我们可以这样设计, 通过 `treasureId` 来与 `Treasure` 进行联合查询, 通过 `seller` 来与 `User` 进行联合查询

## 接口文档

> 对于 `flask` 框架而言, 每一个 `@app.route('xxx')` 修饰的函数都对应了一个页面, 我们只需要补全这些函数, 简单阅读一下前端页面即可设计接口

具体见 `Apifox` 地址 https://www.apifox.cn/apidoc/project-1766606
