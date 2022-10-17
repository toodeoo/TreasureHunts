from flask import Flask, request, render_template, url_for, make_response
import pymongo
import random
from werkzeug.utils import redirect
from hashlib import md5

app = Flask(__name__)

# Connect to Database
# 数据库中，Treasure 的class 0代表工具， 1代表配饰
# 设置存储箱的最大存储量为 20

max_storage = 20


def auto_dropout(person, itemId):
    treasure = db['Treasure']
    item = treasure.find_one({"treasureId": itemId})
    backpack = person.get("backpack")
    if backpack is None:
        backpack = []
    backpack_item = treasure.find({"treasureId": {"$in": backpack}},
                                  {"quality": 1, "treasureId": 1}).sort("quality", pymongo.ASCENDING)
    if backpack_item[0].get("quality") <= item.get("quality"):
        backpack_item[0]["treasureId"] = item_id
        backpack = [i.get("treasureId") for i in backpack_item]
    return backpack


# Checked
@app.route('/')
def index():
    return render_template('index.html')


# Checked
@app.route('/login')
def login():
    if request.method == 'GET':
        name = request.args.get('username')
        pwd = request.args.get('password')
        pwd = md5(pwd.encode('utf-8')).hexdigest()
        person = db['User'].find_one({"username": name})
        if person is None:
            return render_template('sign.html')
        if person.get('pwd') == pwd:
            reps = make_response(render_template('homepage.html', re=[name]))
            reps.set_cookie("username", name)
            return reps


# Checked
@app.route('/homepage')
def homepage():
    re = [request.cookies.get("username")]
    return render_template('homepage.html', re=re)


# Checked
@app.route('/sign')
def sign():
    return render_template('sign.html')


# Checked
@app.route('/signup')
def signup():
    if request.method == 'GET':
        username = request.args.get('username')
        pwd = request.args.get("password")
        pwd = md5(pwd.encode('utf-8'))
        flag = 0
        user = db['User']
        person = user.find_one({"username": username})
        if person != None:
            flag = 1
        else:
            treasure = db['Treasure']
            init_treasure = [treasure.find_one({"name": "帽子"}), treasure.find_one({"name": "充电器"})]
            treasure_list = [init_treasure[0].get('treasureId'), init_treasure[1].get('treasureId')]
            init_luck, init_work = 0, 0
            for i in init_treasure:
                if i.get('class') == 1:
                    init_luck += i.get('property')
                else:
                    init_work += i.get('property')
            user.insert_one({
                "username": username,
                "pwd": pwd.hexdigest(),
                "money": 10,
                "arm": [],
                "backpack": treasure_list,
                "luck": init_luck,
                "work": init_work
            })
        reps = make_response(render_template('signup.html', name=username, tag=flag))
        reps.set_cookie("username", username)
        return reps


# Checked
@app.route('/myinfo')
def myinfo():
    username = request.cookies.get("username")
    user = db["User"].find_one({"username": username})
    money = user.get("money")
    # row1为装备在身上的装备， row2为放在背包里的装备，装备的格式为：装备名称 等级 装备详情
    row1, row2 = [], []
    treasure = db["Treasure"]
    if len(user.get("arm")) > 0:
        for i in user.get("arm"):
            item = treasure.find_one({"treasureId": i})
            row1.append([item.get("name"), item.get("level")])
    if len(user.get("backpack")) > 0:
        for i in user.get("backpack"):
            item = treasure.find_one({"treasureId": i})
            row2.append([item.get("name"), item.get("level"), i])

    return render_template('myinfo.html', name=username, money=money, row1=row1, row2=row2)


# Checked
@app.route('/equip_info')
def equip_info():
    if request.method == 'GET':
        name = request.args.get('equipments')
        treasure = db['Treasure']
        item = treasure.find_one({'name': name})
        equip_type, luck, ability = None, 0, 0
        if item.get('class') == '0':
            equip_type = "工具"
            ability = item.get('property')
        else:
            equip_type = "配饰"
            luck = item.get('property')
        return render_template('equipinfo.html', name=name, id=item.get('treasureId'),
                               equip_type=equip_type, luck=luck, ability=ability, quality=item.get('quality'))


# Checked
@app.route('/sto_info')
def sto_info():
    if request.method == 'GET':
        name = request.args.get('storage')
        treasure = db['Treasure']
        item = treasure.find_one({'name': name})
        equip_type, luck, ability = None, 0, 0
        if item.get('class') == 0:
            equip_type = "工具"
            ability = item.get('property')
        else:
            equip_type = "配饰"
            luck = item.get('property')
        return render_template('stoinfo.html', name=name, id=item.get('treasureId'),
                               equip_type=equip_type, luck=luck, ability=ability, quality=item.get('quality'))


# Checked
@app.route('/take_off')
def take_off():
    treasure = db['Treasure']
    user = db['User']
    tag = 0
    item_name = request.args.get('equipments')
    item = treasure.find_one({"name": item_name})
    item_id = item.get("treasureId")
    person = user.find_one({"username": request.cookies.get('username')})
    armed = person.get("arm")
    armed.remove(item_id)
    backpack = person.get("backpack")
    if backpack is None:
        backpack = []
    if len(backpack) == max_storage:
        tag = 1
        backpack = auto_dropout(person, item)
    else:
        backpack.append(item_id)
    if armed is None:
        armed = []
    user.update_one({"username": person.get("username")},
                    {"$set": {"arm": armed, "backpack": backpack}})
    return render_template('take_off.html', tag=tag)


# Checked
# TODO: 如果物品是放在商场贩卖的话，我们不能装备
@app.route('/take_on')
def take_on():
    user = db['User']
    person = user.find_one({"username": request.cookies.get('username')})
    tag = 0
    treasure = db['Treasure']
    item = treasure.find_one({"name": request.args.get('equipments')})
    item_class = item.get('class')
    armed = person.get('arm')
    if len(armed) == 0:
        armed = [item.get("treasureId")]
        backpack = person.get('backpack')
        backpack.remove(item.get('treasureId'))
        user.update_one({"username": person.get("username")},
                        {"$set": {"arm": armed, "backpack": backpack}})
    elif 3 > len(armed):
        cnt1, cnt2 = 0, 0
        for i in armed:
            if treasure.find_one({"treasureId": i}).get('class') == 0:
                cnt1 += 1
            else:
                cnt2 += 1
        if cnt1 == 1 and item_class == 0:
            tag = 1
        elif cnt2 == 2 and item_class == 1:
            tag = 1
        else:
            item_id = item.get("treasureId")
            armed.append(item_id)
            backpack = person.get('backpack')
            backpack.remove(item_id)
            if backpack is None:
                backpack = []
            user.update_one({"username": request.cookies.get('username')},
                            {"$set": {"backpack": backpack, "arm": armed}})
    else:
        tag = 1
    return render_template('take_on.html', tag=tag)


@app.route('/marinfo')
def marinfo():
    re = []
    market_info = db['Market'].find({})
    treasure = db['Treasure']
    for i in market_info:
        item = treasure.find_one({"treasureId": i.get("treasureId")})
        luck, ability = 0, 0
        if item.get('class') == 0:
            ability = item.get('property')
        else:
            luck = item.get('property')
        re.append([i.get('treasureId'), item.get('name'), item.get('quality'),
                   luck, ability, i.get('price'), i.get('seller')])
    return render_template('marinfo.html', re=re)


@app.route('/buy')
def buy():
    user = db['User']
    market = db['Market']
    tag = 0
    item = market.find_one({"name": request.args.get("name")})
    buyer = user.find_one({"username": request.cookies.get("username")})
    seller = user.find_one({"username": item.get("seller")})

    if buyer.get("username") == seller.get("username"):
        return render_template('buy.html', tag=0)
    if buyer.get("money") < item.get("price"):
        tag = 2
    else:
        seller_backpack = seller.get("backpack")
        seller_money = seller.get("money")
        seller_backpack.remove(item.get("treasureId"))
        seller_money += item.get('price')
        user.update_one({"username": seller.get("username")},
                        {"$set": {"backpack": seller_backpack, "money": seller_money}})

        buyer_money = buyer.get("money")
        buyer_money -= item.get("price")
        if len(buyer.get("backpack")) < max_storage:
            buyer_backpack = buyer.get("backpack")
            buyer_backpack.append(item.get("treasureId"))
        else:
            tag = 1
            buyer_backpack = auto_dropout(buyer, item.get("treasureId"))
        user.update_one({"username": buyer.get("username")},
                        {"$set": {"backpack": buyer_backpack, "money": buyer_money}})
        market.delete_one({"treasureId": item.get("treasureId")})
    return render_template('buy.html', tag=tag)


@app.route('/sell')
def sell():
    re = []
    user = db['User']
    market = db['Market']
    treasure = db['Treasure']

    person = user.find_one({"username": request.args.get('username')})
    backpack = person.get('backpack')
    item_list = treasure.find({"treasureId": {"$in": backpack}})
    for i in item_list:
        luck, ability = 0, 0
        if i.get('class') == 0:
            ability = i.get("property")
        else:
            luck = i.get("property")
        re.append([i.get("treasureId"), i.get("name"), i.get("quality"), luck, ability])
    return render_template('sell.html', re=re)


@app.route('/sell_it')
def sell_it():
    price = request.args.get('price')
    item_name = request.args.get('name')
    treasure = db['Treasure']
    market = db['Market']
    item_id = treasure.find_one({"name": item_name}).get("treasureId")
    market.insert_one({"treasureId": item_id, "price": price, "seller": request.cookies.get("username")})
    return render_template('sellinfo.html')


@app.route('/look_for_treasure')
def look_for_treasure():
    return render_template('look_for_treasure.html', equip_name='手套', tag=0)


@app.route('/look_for_money')
def look_for_money():
    return render_template('look_for_money.html', money=10)


app.config['DEBUG'] = True
app.secret_key = '123456'

if __name__ == '__main__':
    setting = {
        'ip': "mongodb://127.0.0.1:27017",
        'db_name': 'Game'
    }
    client = pymongo.MongoClient(setting['ip'])
    db = client[setting['db_name']]
    app.run(host='127.0.0.1', port=5005)
