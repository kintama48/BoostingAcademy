import datetime
import json
import os
import sys

import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio

from discord.utils import get

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)


class Claim(commands.Cog, name="claim"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="new", description="Opens a new ticket")
    @commands.has_permissions(administrator=True)
    async def new(self, ctx):
        questions = ['Boost Info?', 'Pay?', 'Delivery?']

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        index = 1
        answers = []
        question_message = None
        for question in questions:
            embed = discord.Embed(
                title=f"**{question}**                        ",
                color=0x036bfc, timestamp=datetime.datetime.now()
            ).set_footer(icon_url=self.bot.user.avatar.url, text="New Request ")
            if index == 1:
                question_message = await ctx.reply(embed=embed)
            else:
                await question_message.edit(embed=embed)

            try:
                user_response = await self.bot.wait_for("message", timeout=120, check=check)
                await user_response.delete()
            except asyncio.TimeoutError:
                await ctx.send(embed=discord.Embed(
                    title="Error",
                    color=0x036bfc,
                    description="You took too long to answer this question"
                ))
                return
            else:
                answers.append(user_response.content)
                index += 1

        boost_info = answers[0]
        pay = answers[1]
        delivery = answers[2]

        request_channel = get(ctx.guild.channels, id=config["channel"]["request"])
        request_embed = discord.Embed(title=f"New Request                       ",
                                      timestamp=datetime.datetime.now(), color=0x6b1fcf) \
            .add_field(name="Boost Info", value=boost_info, inline=True) \
            .add_field(name="Delivery", value=delivery, inline=True) \
            .add_field(name="Pay", value=pay, inline=False) \
            .set_footer(icon_url=self.bot.user.avatar.url, text='Boosting Academy ©')

        async def button_callback(interaction: discord.Interaction):
            not_allowed_roles = [role for role in ctx.guild.roles if int(role.id) in config["not_allowed_roles"]]
            owner_role = get(ctx.guild.roles, id=870482165501161493)
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True),
                owner_role: discord.PermissionOverwrite(read_messages=True)
            }

            for role in not_allowed_roles:
                overwrites[role] = discord.PermissionOverwrite(read_messages=False)

            config["request_count"] += 1
            channel = await ctx.guild.create_text_channel(f'🎟️ - request - {config["request_count"] + 1}',
                                                          overwrites=overwrites)

            with open('config.json', "w") as outfile:
                json.dump(config, outfile)

            view.remove_item(button)
            button.disabled = True
            button.style = discord.ButtonStyle.gray
            view.add_item(button)

            request_channel_info = discord.Embed(title=f"Request",
                                                 description=f"{interaction.user.mention}\n\n"
                                                             f" Your claim request has"
                                                             f" been granted.\n ", timestamp=datetime.datetime.now(),
                                                 color=0x6b1fcf) \
                .add_field(name="Boost Info", value=boost_info, inline=True) \
                .add_field(name="Delivery", value=delivery, inline=True) \
                .add_field(name="Pay", value=pay, inline=False)\
                .set_footer(icon_url=self.bot.user.avatar.url, text='Boosting Academy ©')

            await interaction.response.edit_message(view=view)
            await channel.send(content=owner_role.mention,
                               embed=request_channel_info)

        button = Button(label='Claim', style=discord.ButtonStyle.green, emoji="🎟️")
        button.callback = button_callback
        view = View()
        view.add_item(button)

        await question_message.edit(embed=discord.Embed(title="Operation Successful",
                                                        description=f"Claim ticket created in {request_channel.mention}!",
                                                        timestamp=datetime.datetime.now())
                                    .set_footer(icon_url=self.bot.user.avatar.url, text='Boosting Academy ©'))
        await request_channel.send(embed=request_embed, view=view)


def setup(bot):
    bot.add_cog(Claim(bot))
