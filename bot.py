import discord
from discord.ext import commands
from discord.ui import Button, View, Select
import random
import os
import sqlite3

# --- ตั้งค่าฐานข้อมูล SQLite ---
def init_db():
    conn = sqlite3.connect('army_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id INTEGER PRIMARY KEY, rank TEXT, exp INTEGER, money INTEGER, energy INTEGER)''')
    conn.commit()
    conn.close()

def get_user_stats(user_id):
    conn = sqlite3.connect('army_data.db')
    c = conn.cursor()
    c.execute("SELECT rank, exp, money, energy FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if row is None:
        # ถ้าไม่มีข้อมูล ให้สร้างใหม่
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (user_id, "พลทหาร", 0, 0, 100))
        conn.commit()
        row = ("พลทหาร", 0, 0, 100)
    conn.close()
    return {"rank": row[0], "exp": row[1], "money": row[2], "energy": row[3]}

def save_user_stats(user_id, stats):
    conn = sqlite3.connect('army_data.db')
    c = conn.cursor()
    c.execute("UPDATE users SET rank = ?, exp = ?, money = ?, energy = ? WHERE user_id = ?",
              (stats["rank"], stats["exp"], stats["money"], stats["energy"], user_id))
    conn.commit()
    conn.close()

# --- ตั้งค่า Bot ---
TOKEN = os.getenv('MTUwMTQ0MzUxNDI1MTM1MDIxOA.Gpmgux.4vlj7IBaX5IxFU7e5qTCDJF3oPvIGzfSS9oYGU')
ANGRY_SHOUTS = [
    "จ่าสั่งให้ซ่อม! มัวแต่เหม่อหาใครฮะ?! 'พุ่งหลัง 50 ปฏิบัติ!'",
    "วินัยอยู่ที่ไหน! ทำผิดระเบียบแบบนี้ต้อง 'แดก' เท่านั้น!",
    "นี่มันพลทหารหรือนางรำ! ยึดพื้นค้างไว้จนกว่าจ่าจะพอใจ!",
    "สายตาหลุกหลิกนะเราน่ะ! ไปวิ่งรอบสนาม 5 รอบ เดี๋ยวนี้!",
    "นิ่มเป็นสำลีแบบนี้จะไปรบกับใครได้! 'หมอบ... ลุก... หมอบ... ลุก!'"
]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

class ShopSelect(Select):
    def __init__(self, user_id):
        self.user_id = user_id
        options = [
            discord.SelectOption(label="เครื่องดื่มชูกำลัง", description="50฿ (+30 พลัง)", emoji="🥤"),
            discord.SelectOption(label="ยาหม่องจ่าแดง", description="30฿ (+15 พลัง)", emoji="🧴"),
            discord.SelectOption(label="อามยศใหม่", description="150฿ (+50 EXP)", emoji="🎖️")
        ]
        super().__init__(placeholder="🛒 ร้านสวัสดิการ (PX)", options=options)

    async def callback(self, interaction: discord.Interaction):
        stats = get_user_stats(interaction.user.id)
        item = self.values[0]
        
        if item == "เครื่องดื่มชูกำลัง" and stats["money"] >= 50:
            stats["money"] -= 50
            stats["energy"] = min(100, stats["energy"] + 30)
            msg = "🥤 ซดเครื่องดื่มเข้าไป ดีดจัด!"
        elif item == "ยาหม่องจ่าแดง" and stats["money"] >= 30:
            stats["money"] -= 30
            stats["energy"] = min(100, stats["energy"] + 15)
            msg = "🧴 ทายาหม่องแล้วสบายตัว"
        elif item == "อามยศใหม่" and stats["money"] >= 150:
            stats["money"] -= 150
            stats["exp"] += 50
            msg = "🎖️ ซื้ออามมาติดแขน ดูดีมีราศี!"
        else:
            return await interaction.response.send_message("เงินไม่พอ!", ephemeral=True)

        save_user_stats(interaction.user.id, stats)
        await update_embed(interaction, stats, msg)

class ArmyLifeView(View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.add_item(ShopSelect(user_id))

    @discord.ui.button(label="🏋️ ฝึกร่างกาย", style=discord.ButtonStyle.primary, row=1)
    async def train(self, interaction: discord.Interaction, button: Button):
        stats = get_user_stats(interaction.user.id)
        if stats["energy"] < 25:
            return await interaction.response.send_message("พลังงานไม่พอ!", ephemeral=True)
        
        if random.random() < 0.20:
            shout = random.choice(ANGRY_SHOUTS)
            stats["energy"] -= 30
            save_user_stats(interaction.user.id, stats)
            embed = discord.Embed(title="💢 โดนสั่งซ่อม!", description=f"**จ่า:** *\"{shout}\"*", color=discord.Color.red())
            return await interaction.response.edit_message(embed=embed, view=self)

        gain_exp = random.randint(15, 25)
        stats["exp"] += gain_exp
        stats["energy"] -= 20
        save_user_stats(interaction.user.id, stats)
        await update_embed(interaction, stats, f"📈 ได้รับ {gain_exp} EXP")

    @discord.ui.button(label="🛡️ เข้าเวร", style=discord.ButtonStyle.success, row=1)
    async def work(self, interaction: discord.Interaction, button: Button):
        stats = get_user_stats(interaction.user.id)
        if stats["energy"] < 15:
            return await interaction.response.send_message("ง่วงนอน...", ephemeral=True)
        
        pay = random.randint(60, 120)
        stats["money"] += pay
        stats["energy"] -= 15
        save_user_stats(interaction.user.id, stats)
        await update_embed(interaction, stats, f"💰 ได้เบี้ยเลี้ยง {pay} บาท")

    @discord.ui.button(label="💤 พักผ่อน", style=discord.ButtonStyle.secondary, row=1)
    async def rest(self, interaction: discord.Interaction, button: Button):
        stats = get_user_stats(interaction.user.id)
        stats["energy"] = min(100, stats["energy"] + 45)
        save_user_stats(interaction.user.id, stats)
        await update_embed(interaction, stats, "💤 พักผ่อนเรียบร้อย")

async def update_embed(interaction, stats, log_msg):
    if stats["exp"] >= 300 and stats["rank"] == "พลทหาร":
        stats["rank"] = "สิบตรี"
        log_msg = "🎊 เลื่อนยศเป็น สิบตรี!"
        save_user_stats(interaction.user.id, stats)

    embed = discord.Embed(title="🎖️ ระบบจำลองชีวิตกองทัพ", color=discord.Color.dark_green())
    embed.add_field(name="🎖️ ยศ", value=stats["rank"], inline=True)
    embed.add_field(name="💰 เงิน", value=f"{stats['money']} ฿", inline=True)
    embed.add_field(name="⚡ พลัง", value=f"{stats['energy']}/100", inline=True)
    embed.set_footer(text=f"บันทึก: {log_msg}")
    await interaction.response.edit_message(embed=embed, view=ArmyLifeView(interaction.user.id))

@bot.event
async def on_ready():
    init_db()
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def start(ctx):
    get_user_stats(ctx.author.id) # ตรวจสอบ/สร้างข้อมูล
    embed = discord.Embed(title="🎖️ รายงานตัวเข้ากรม", description="ข้อมูลของคุณจะถูกบันทึกไว้ตลอดไป", color=discord.Color.blue())
    await ctx.send(embed=embed, view=ArmyLifeView(ctx.author.id))

if TOKEN:
    bot.run(TOKEN)
            
