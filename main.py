import discord
from discord.ext import commands
import requests
import json
from tabulate import tabulate
import asyncio
from webserver import keep_alive
from os import system
import time

bot = commands.Bot(command_prefix=".", help_command=None)


@bot.command()
async def payout(ctx, x: float):
    y = x - (x * (9.5 / 100) + 20)
    final = y - (y * (2.9 / 100))
    payout = f'{final:.2f}'
    text = "Payout USD: "
    sign = "$"
    reply = text + sign + payout

    link = f'https://wise.com/gateway/v3/price?sourceAmount={payout}&sourceCurrency=USD&targetCurrency=MYR&markers=FCF_PRICING'
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64;     x64) AppleWebKit/537.36 (KHTML, like Gecko)    Chrome/92.0.4515.159 Safari/537.36"}

    requests_data = requests.get(link, headers=headers).json()

    list = []
    for item in requests_data:
        name = item['targetAmount']
        y = str(name)
        # for item in y:
        list.append(item)

    z = (list[60])
    y = z['targetAmount']
    transferwise = ("Payout MYR: RM%.2f " % y)
    wiseUrl = f'https://wise.com/gb/pricing/borderless-send?source=USD&target=MYR&payInMethod=BALANCE&sourceAmount={payout}'
    embed = discord.Embed(title="Payout Calculator", url=wiseUrl, color=0x00ff00)
    embed.add_field(name="Goat", value="```" + reply + "```", inline=False)
    embed.add_field(name="Wise USD > MYR", value="```" + transferwise + "```", inline=False)
    await ctx.send(embed=embed)


# Goat

selected = 0
numResults = 0


@bot.command()
async def lookup(selection, keywords, ctx):
    json_string = json.dumps({
        "params": f"distinct=true&facetFilters=()&facets=%5B%22size%22%5D&hitsPerPage=20&numericFilters=%5B%5D&page=0&query={keywords}"})
    byte_payload = bytes(json_string, 'utf-8')
    params = {
        "x-algolia-agent": "Algolia for vanilla JavaScript 3.25.1",
        "x-algolia-application-id": "2FWOTDVM2O",
        "x-algolia-api-key": "ac96de6fef0e02bb95d433d8d5c7038a"
    }
    header = {
        'accept': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        'accept-language': 'en-us',
        'accept-encoding': 'br,gzip,deflate'
    }
    with requests.Session() as s:
        r = s.post("https://2fwotdvm2o-dsn.algolia.net/1/indexes/product_variants_v2/query", params=params,
                   verify=False, data=byte_payload, timeout=30)
    results = r.json()["hits"][selection]
    generalAPI = f"https://www.goat.com/api/v1/product_templates/{results['slug']}/show_v2"
    offerAPI = f"https://www.goat.com/api/v1/highest_offers?productTemplateId={results['id']}"
    askAPI = f"https://www.goat.com/api/v1/product_variants?productTemplateId={results['slug']}"
    general = requests.get(generalAPI, headers=header).json()
    bids = requests.get(offerAPI, headers=header).json()
    asks = requests.get(askAPI, headers=header).json()
    link = f"https://goat.com/sneakers/{results['slug']}"

    priceDict = {}
    for size in general['sizeOptions']:
        priceDict[float(size["value"])] = {"ask": 0, "bid": 0}
    for ask in general['availableSizesNewV2']:
        if ask[2] == "good_condition":
            priceDict[float(ask[0])]["ask"] = ask[1][:-2]
    for bid in bids:
        if bid["size"] in priceDict:
            priceDict[bid["size"]]["bid"] = str(bid["offerAmountCents"]["amountUsdCents"])[:-2]
    for ask in asks:
        if ask["boxCondition"] == "good_condition":
            priceDict[ask["size"]]["ask"] = str(ask["lowestPriceCents"]["amountUsdCents"])[:-2]

    if general["productCategory"] == "clothing":
        priceDict2 = {}
        for size in priceDict:
            for size2 in general["sizeOptions"]:
                if size == size2["value"]:
                    priceDict2[size2["presentation"].upper()] = priceDict[size]
        priceDict = priceDict2

    priceDict = {k: v for k, v in priceDict.items() if v["ask"] != 0 or v["bid"] != 0}

    table = []
    table.append(["Size", "Lowest Ask", "Highest Bid"])
    for size, price in priceDict.items():
        table.append([size, f"${price['ask']}", f"${price['bid']}"])

    tabulated = "```" + tabulate(table, headers="firstrow", numalign="center", stralign="center",
                                 tablefmt="simple") + "```"

    embed = discord.Embed(title='GOAT App Price Checker', color=0x13e79e)
    embed.set_thumbnail(url=general['mainGlowPictureUrl'])
    embed.set_footer(text='RealBeen ❤')
    embed.add_field(name='Product Name', value=f"[{general['name']}]({link})", inline=False)
    embed.add_field(name='SKU', value=f"{general['sku']}", inline=True)
    try:
        embed.add_field(name='Release Date', value=f"{results['release_date'].split('T')[0]}", inline=True)
    except:
        embed.add_field(name='Release Date', value=f"{results['release_date']}", inline=True)
    embed.add_field(name='Prices', value=tabulated, inline=False)
    await ctx.send(embed=embed)


@bot.event
async def on_ready():
    print('GOAT Discord Bot is ready.')


@bot.command(pass_context=True)
async def logout(ctx):
    await bot.logout()


@bot.command(pass_context=True)
async def goat(ctx, *args):
    keywords = ''
    for word in args:
        keywords += word + '%20'
    json_string = json.dumps({
        "params": f"distinct=true&facetFilters=()&facets=%5B%22size%22%5D&hitsPerPage=20&numericFilters=%5B%5D&page=0&query={keywords}"})
    byte_payload = bytes(json_string, 'utf-8')
    params = {
        "x-algolia-agent": "Algolia for vanilla JavaScript 3.25.1",
        "x-algolia-application-id": "2FWOTDVM2O",
        "x-algolia-api-key": "ac96de6fef0e02bb95d433d8d5c7038a"
    }
    with requests.Session() as s:
        r = s.post("https://2fwotdvm2o-dsn.algolia.net/1/indexes/product_variants_v2/query", params=params,
                   verify=False, data=byte_payload, timeout=30)
        numResults = len(r.json()["hits"])
        results = r.json()["hits"]

    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

    def check(reaction, user):
        if str(reaction.emoji) in emojis:
            global selected
            selected = emojis.index(str(reaction.emoji))
        return user == ctx.author and str(reaction.emoji) in emojis

    if numResults == 1:
        await lookup(0, keywords, ctx)
    elif numResults >= 2 and numResults <= 10:
        resultsText = ""
        for i in range(len(results)):
            resultsText += f"{i + 1}. {results[i]['name']}\n"
        msg = await ctx.send(
            'Multiple products found. React to select the correct product:\n' + "```" + resultsText + "```")
        for i in range(len(results)):
            await msg.add_reaction(emojis[i])
        try:
            await bot.wait_for('reaction_add', timeout=30.0, check=check)
            await lookup(selected, keywords, ctx)
            # This automatically deletes the selection message
            # await msg.delete()
        except asyncio.TimeoutError:
            await ctx.send('Took too long to select an option. Please try again.')
    elif numResults == 0:
        await ctx.send('No products found. Please try again.')
    elif numResults > 10:
        await ctx.send('Too many products found. Please try again.')


keep_alive()

TOKEN = ''


def run():
    try:
        bot.run(TOKEN)
    # except discord.errors.HTTPException:
    except:
        print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")
        f = open("logs.txt", "a")
        f.write("Restart" + "\n")
        f.close()
        system("python restarter.py")
        system('kill 1')


while True:
    run()
    time.sleep(1800)
    print("Done")
