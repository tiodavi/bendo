from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime, date
import pytz

app = Flask(__name__)

# 設定台灣時區
tw_tz = pytz.timezone('Asia/Taipei')

# 創建資料庫和表格
def init_db():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    # 先刪除舊表
    c.execute('DROP TABLE IF EXISTS orders')
    # 建立新表
    c.execute('''
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            lunch_name TEXT NOT NULL,
            price INTEGER NOT NULL,
            remarks TEXT,
            order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            payment_status TEXT DEFAULT '未付款',
            order_status TEXT DEFAULT '開放中'
        )
    ''')
    conn.commit()
    conn.close()

# 初始化資料庫
#init_db()

@app.route('/delete/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('DELETE FROM orders WHERE id = ?', (order_id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/toggle_order_status', methods=['POST'])
def toggle_order_status():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('UPDATE orders SET order_status = "已收單" WHERE order_status IS NULL OR order_status = "開放中"')
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/update_payment/<int:order_id>', methods=['POST'])
def update_payment(order_id):
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('UPDATE orders SET payment_status = "已付款" WHERE id = ?', (order_id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/update_remarks/<int:order_id>', methods=['POST'])
def update_remarks(order_id):
    new_remarks = request.form['new_remarks']
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    c.execute('UPDATE orders SET remarks = ? WHERE id = ?', (new_remarks, order_id))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 獲取表單數據
        user_name = request.form['userName']
        lunch_name = request.form['lunchName']
        price = request.form['price']
        remarks = request.form['remarks']
        
        # 存入資料庫
        conn = sqlite3.connect('orders.db')
        c = conn.cursor()
        current_time = datetime.now(tw_tz)
        order_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
        c.execute('''
            INSERT INTO orders (user_name, lunch_name, price, remarks, order_status, order_time)
            VALUES (?, ?, ?, ?, "開放中", ?)
        ''', (user_name, lunch_name, price, remarks, order_time))
        conn.commit()
        conn.close()
        
        return redirect('/')
    
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    
    # 獲取今天的日期範圍
    today = date.today()
    today_start = f"{today} 00:00:00"
    today_end = f"{today} 23:59:59"
    
    # 修改查詢只顯示今天的訂單
    c.execute('''
        SELECT id, user_name, lunch_name, price, remarks, order_time, payment_status, order_status 
        FROM orders 
        WHERE date(order_time) = date('now', 'localtime')
        ORDER BY order_time DESC
    ''')
    
    orders = [
        {
            'id': row[0],
            'user_name': row[1],
            'lunch_name': row[2],
            'price': row[3],
            'remarks': row[4],
            'order_time': row[5],
            'payment_status': row[6],
            'order_status': row[7]
        }
        for row in c.fetchall()
    ]
    conn.close()
    
    # 計算今日總計
    today_total = sum(order['price'] for order in orders)
    
    return render_template('index.html', 
                         orders=orders, 
                         today_total=today_total,
                         today_date=today.strftime('%Y-%m-%d'))

@app.route('/store1')
def store1():
    return render_template('store1.html')

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/order', methods=['POST'])
def order():
    if request.method == 'POST':
        meal_info = request.form['meal'].split(',')
        user_name = request.form['userName']
        remarks = request.form['remarks']
        
        lunch_name = meal_info[0]
        price = int(meal_info[1])
        
        conn = sqlite3.connect('orders.db')
        c = conn.cursor()
        current_time = datetime.now(tw_tz)
        order_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
        c.execute('''
            INSERT INTO orders (user_name, lunch_name, price, remarks, order_status, order_time)
            VALUES (?, ?, ?, ?, "開放中", ?)
        ''', (user_name, lunch_name, price, remarks, order_time))
        conn.commit()
        conn.close()
        
        return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
