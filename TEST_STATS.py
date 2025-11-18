import discord
from discord.ext import commands
from discord.ui import View, Button
import json
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

ID_PLAN = 1439247414685859992
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "plan.json")

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return {}  # fichier vide → dictionnaire vide
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

plans = load_data()

def make_text(map_name, point, description, up, down):
    total = up + down
    percent = 0 if total == 0 else round((up / total) * 100)
    return (f"**Stratégie CODM — {map_name} {point}**\n\n"
            f"{description}\n\n"
            f"(✅ : {up}, ❌ : {down} — **{percent}% réussite**)")

class VoteView(View):
    def __init__(self, message_id):
        super().__init__(timeout=None)
        self.message_id = str(message_id)

    @discord.ui.button(label="Voter +1", style=discord.ButtonStyle.success)
    async def vote_positive(self, interaction: discord.Interaction, button: Button):
        plans[self.message_id]["up"] += 1
        save_data(plans)

        await interaction.response.edit_message(
            content=make_text(
                plans[self.message_id]["map"],
                plans[self.message_id]["point"],
                plans[self.message_id]["description"],
                plans[self.message_id]["up"],
                plans[self.message_id]["down"]
            ),
            view=self
        )

    @discord.ui.button(label="Voter -1", style=discord.ButtonStyle.danger)
    async def vote_negative(self, interaction: discord.Interaction, button: Button):
        plans[self.message_id]["down"] += 1
        save_data(plans)

        await interaction.response.edit_message(
            content=make_text(
                plans[self.message_id]["map"],
                plans[self.message_id]["point"],
                plans[self.message_id]["description"],
                plans[self.message_id]["up"],
                plans[self.message_id]["down"]
            ),
            view=self
        )

@bot.command()
async def top(ctx, map_name=None, point=None):
    if not plans:
        await ctx.reply("Aucune stratégie enregistrée.")
        return

    # Filtrage par map et/ou point si précisé
    filtered = [
        data for data in plans.values()
        if (not map_name or data["map"].lower() == map_name.lower())
        and (not point or data["point"].lower() == point.lower())
    ]

    if not filtered:
        await ctx.reply("Aucune stratégie trouvée avec ces critères.")
        return

    # Classement : meilleur taux de réussite
    filtered.sort(key=lambda x: (x["up"] / (x["up"] + x["down"])) if (x["up"] + x["down"]) > 0 else 0, reverse=True)

    result = "\n\n".join([
        f"**{d['map']} {d['point']}** — {round((d['up']/(d['up']+d['down'])*100)) if d['up']+d['down'] else 0}% "
        f"(+{d['up']}/-{d['down']})\n→ {d['description']}"
        for d in filtered[:10]
    ])

    await ctx.reply(f"🏆 **Top stratégies CODM**\n\n{result}")

@bot.command()
async def plan(ctx, map_name: str, point: str, *, description: str):
    channel = bot.get_channel(ID_PLAN) or ctx.channel
    message = await channel.send(
        make_text(map_name, point, description, 0, 0),
        view=VoteView("temp")
    )

    plans[str(message.id)] = {
        "map": map_name,
        "point": point,
        "description": description,
        "up": 0,
        "down": 0
    }
    save_data(plans)

    await message.edit(view=VoteView(message.id))
    await ctx.reply(f"Stratégie enregistrée : ID `{message.id}`")

@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")

bot.run(os.getenv("DISCORD_TOKEN"))



