from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# 1. Database Setup
def init_db():
    conn = sqlite3.connect('business.db')
    c = conn.cursor()
    # Create products table
    c.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, price TEXT)')
    # Create the NEW messages table
    c.execute('CREATE TABLE IF NOT EXISTS messages (name TEXT, phone TEXT, message TEXT)')
    
    c.execute('SELECT count(*) FROM products')
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO products (name, price) VALUES ('Coconut', '45,000')")
        c.execute("INSERT INTO products (name, price) VALUES ('Mango', '150')")
        conn.commit()
    conn.close()

init_db()

# 2. Customer Website & Receiving Messages
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # This saves the message when a customer clicks 'Send'
        buyer_name = request.form['buyer_name']
        buyer_phone = request.form['buyer_phone']
        buyer_msg = request.form['buyer_message']
        
        conn = sqlite3.connect('business.db')
        c = conn.cursor()
        c.execute("INSERT INTO messages (name, phone, message) VALUES (?, ?, ?)", (buyer_name, buyer_phone, buyer_msg))
        conn.commit()
        conn.close()
        return redirect(url_for('home')) # Reloads the page safely

    # Fetch live prices
    conn = sqlite3.connect('business.db')
    c = conn.cursor()
    c.execute("SELECT price FROM products WHERE name='Coconut'")
    coconut_price = c.fetchone()[0]
    c.execute("SELECT price FROM products WHERE name='Mango'")
    mango_price = c.fetchone()[0]
    conn.close()
    
    return render_template('index.html', coconut_price=coconut_price, mango_price=mango_price)

# 3. Admin Panel & Reading Messages
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        # Updating prices
        if request.form.get('password') == 'admin123': 
            new_coco_price = request.form['coconut_price']
            new_mango_price = request.form['mango_price']
            
            conn = sqlite3.connect('business.db')
            c = conn.cursor()
            c.execute("UPDATE products SET price=? WHERE name='Coconut'", (new_coco_price,))
            c.execute("UPDATE products SET price=? WHERE name='Mango'", (new_mango_price,))
            conn.commit()
            conn.close()
            return redirect(url_for('admin')) 
        else:
            return "Wrong Password!"
            
    # Fetch all customer messages to show in the admin panel
    conn = sqlite3.connect('business.db')
    c = conn.cursor()
    c.execute("SELECT name, phone, message FROM messages")
    all_messages = c.fetchall()
    conn.close()
            
    return render_template('admin.html', messages=all_messages)

if __name__ == '__main__':
    app.run(debug=True)