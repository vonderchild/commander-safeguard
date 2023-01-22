import asyncio
import discord
import os
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix='!', intents=intents)


@client.command(name="tempmute")
@commands.has_permissions(kick_members=True)
async def tempmute(ctx, member: discord.Member, time: int, d, *, reason=None):
    guild = ctx.guild
    muted = discord.utils.get(guild.roles, name="Muted")
    if not muted:
        muted = await guild.create_role(name="Muted")
        for channel in guild.channels:
            await channel.set_permissions(muted, speak=False, send_messages=False, read_message_history=True,
                                          read_messages=False)

    for role in guild.roles:
        if role.name == "Muted":
            await member.add_roles(muted, reason=reason)

            embed = discord.Embed(title="muted!", description=f"{member.mention} has been temporarily muted ",
                                  colour=discord.Colour.light_gray())
            embed.add_field(name="reason:", value=reason, inline=False)
            embed.add_field(name="time left for the mute:", value=f"{time}{d}", inline=False)
            await ctx.send(embed=embed)

            if d == "s":
                await asyncio.sleep(time)

            if d == "m":
                await asyncio.sleep(time * 60)

            if d == "h":
                await asyncio.sleep(time * 60 * 60)

            if d == "d":
                await asyncio.sleep(time * 60 * 60 * 24)

            await member.remove_roles(muted)

            embed = discord.Embed(title="unmute (temp) ", description=f"unmuted -{member.mention} ",
                                  colour=discord.Colour.light_gray())
            await ctx.send(embed=embed)

            return


@client.command(name="kick")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'User {member} has been kicked.')


@client.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'User {member} has been banned')


@client.command()
@commands.has_permissions(administrator=True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split("#")

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.mention}')
            return


@client.event
async def on_member_join(member):
    embed = discord.Embed(title=f"Welcome {member.name}",
                          description=f"Thanks for joining {member.guild.name}'s official Discord server!")
    embed.set_thumbnail(url=member.avatar_url)
    channel = discord.utils.get(client.get_all_channels(), name='general')
    await channel.send(embed=embed)


@client.event
async def on_ready():
    # channel_id = 1312312412421421421
    # channel = await client.fetch_channel(channel_id)
    channel = discord.utils.get(client.get_all_channels(), name='general')

    embed = discord.Embed(title=f"React 💻 for HackWeek Role")
    embed.set_thumbnail(url="https://i.imgur.com/ZFrTiat.png")
    sent_message = await channel.send(embed=embed)
    await sent_message.add_reaction("💻")

    @client.event
    async def on_raw_reaction_add(reaction):
        if reaction.message_id == sent_message.id:
            if reaction.emoji.name == "💻":
                user = reaction.member
                role = discord.utils.get(user.guild.roles, name="HackWeek 2023")
                if not role:
                    role = await user.guild.create_role(name="HackWeek 2023")

                await user.add_roles(role)

    @client.event
    async def on_raw_reaction_remove(reaction):
        if reaction.message_id == sent_message.id:
            if reaction.emoji.name == "💻":
                user_id = reaction.user_id  # using user_id since reaction does not return member here
                guild_id = reaction.guild_id

                guild = client.get_guild(guild_id)
                user = guild.get_member(user_id)
                role = discord.utils.get(user.guild.roles, name="HackWeek 2023")

                if not role:
                    role = await user.guild.create_role(name="HackWeek 2023")

                await user.remove_roles(role)


my_secret = os.environ['token']
client.run(my_secret)
