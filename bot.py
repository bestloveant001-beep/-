import discord
from discord.ext import commands
from discord.ui import Button, View, Select
import random
import os  # เพิ่มมาเพื่อดึง Token จากระบบ

# --- ดึง Token จาก Environment Variable ---
TOKEN = os.getenv('DISCORD_TOKEN')

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

users_data = {}

def get_user_stats(user_id):
    if user_id not in users_data:
        users_data[user_id] = {"rank": "พลทหาร", "exp": 0, "money": 0, "energy": 100}
    return users_data[user_id]

# (ส่วนคลาส ShopSelect, ArmyLifeView และฟังก์ชัน update_embed ใช้โค้ดเดิมจากด้านบนได้เลยครับ)
# ... [ยกโค้ดคลาสจากคำตอบก่อนหน้ามาใส่ตรงนี้] ...

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def start(ctx):
    stats = get_user_stats(ctx.author.id)
    embed = discord.Embed(title="🎖️ รายงานตัวเข้ากรม", description="เลือกกิจกรรมด้านล่าง", color=discord.Color.blue())
    view = ArmyLifeView(ctx.author.id)
    await ctx.send(embed=embed, view=view)

if TOKEN:
    bot.run(TOKEN)
else:
    print("Error: No DISCORD_TOKEN found!")
  
