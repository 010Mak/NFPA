import os
from PIL import Image, ImageDraw, ImageFont
import discord
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

SPECIAL_HAZARDS = [
    {"name": "Acid", "value": "ACID"},
    {"name": "Alkaline", "value": "ALK"},
    {"name": "Corrosive", "value": "COR"},
    {"name": "Oxidizer", "value": "OX"},
    {"name": "Radioactive", "value": "RADIO"},
    {"name": "Use No Water", "value": "W"}
]

def generate_nfpa(health, flammability, reactivity, special):
    special_icon_dict = {
        "ACID": "acid.png",
        "ALK": "alk.png",
        "COR": "cor.png",
        "OX": "oxy.png",
        "RADIO": "radio.png",
        "W": "usenowater.png"
    }
    template_path = "blank_diamond.png"
    if not os.path.exists(template_path):
        raise FileNotFoundError("Template image 'blank_diamond.png' not found.")
    image = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", 600)
    except IOError:
        font = ImageFont.load_default()
    health_coords = (512, 1024)
    flammability_coords = (1024, 512)
    reactivity_coords = (1536, 1024)
    special_coords = (1024, 1536)
    draw.text(health_coords, health, font=font, fill="black", anchor="mm")
    draw.text(flammability_coords, flammability, font=font, fill="black", anchor="mm")
    draw.text(reactivity_coords, reactivity, font=font, fill="black", anchor="mm")
    if special:
        icon_filename = special_icon_dict.get(special)
        if icon_filename:
            icon_path = os.path.join("icons", icon_filename)
            if os.path.exists(icon_path):
                icon_image = Image.open(icon_path).convert("RGBA")
                icon_x = 1024 - (450 // 2)
                icon_y = 1536 - (450 // 2)
                image.paste(icon_image, (icon_x, icon_y), icon_image)
            else:
                draw.text(special_coords, special, font=font, fill="black", anchor="mm")
        else:
            draw.text(special_coords, special, font=font, fill="black", anchor="mm")
    output_path = "nfpa_preview.png"
    image.save(output_path)
    return output_path

@bot.tree.command(name="nfpa", description="Generate an NFPA diamond")
@app_commands.describe(
    health="Health hazard level (0-4)",
    flammability="Flammability hazard level (0-4)",
    reactivity="Reactivity hazard level (0-4)",
    special="Special hazard (optional)"
)
@app_commands.choices(
    special=[app_commands.Choice(name=hazard["name"], value=hazard["value"]) for hazard in SPECIAL_HAZARDS]
)
async def nfpa(interaction: discord.Interaction, health: int, flammability: int, reactivity: int, special: str = ""):
    try:
        if not (0 <= health <= 4):
            await interaction.response.send_message("Health must be between 0 and 4.", ephemeral=True)
            return
        if not (0 <= flammability <= 4):
            await interaction.response.send_message("Flammability must be between 0 and 4.", ephemeral=True)
            return
        if not (0 <= reactivity <= 4):
            await interaction.response.send_message("Reactivity must be between 0 and 4.", ephemeral=True)
            return
        output_path = generate_nfpa(str(health), str(flammability), str(reactivity), special.upper())
        embed = discord.Embed(
            title="NFPA Diamond Preview",
            description=f"**Health:** {health}\n**Flammability:** {flammability}\n**Reactivity:** {reactivity}\n**Special Hazard:** {special or 'None'}",
            color=discord.Color.blue()
        )
        embed.set_image(url="attachment://nfpa_preview.png")
        embed.set_footer(text="Open the image and press 'Save' to download it.")
        await interaction.response.send_message(embed=embed, file=discord.File(output_path))
        os.remove(output_path)
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

@bot.tree.command(name="help", description="Get a guide for labeling NFPA signs")
async def help(interaction: discord.Interaction):
    try:
        help_image_path = "help.png"
        if not os.path.exists(help_image_path):
            raise FileNotFoundError("The 'help.png' file is missing from the main directory.")
        embed = discord.Embed(
            title="NFPA Sign Labeling Guide",
            description="This image explains how to label NFPA signs correctly.",
            color=discord.Color.green()
        )
        embed.set_image(url="attachment://help.png")
        embed.set_footer(text="For more info, visit the official NFPA documentation.")
        await interaction.response.send_message(embed=embed, file=discord.File(help_image_path))
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
bot.run(TOKEN)