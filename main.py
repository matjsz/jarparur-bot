import discord, asyncio, os, json, time, random, string
from discord import guild
from discord import player
from discord.enums import UserContentFilter
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from discord import embeds
from discord.ext import commands, tasks
from datetime import date, datetime

# Discord BOT Config
client = commands.Bot(command_prefix = 'r?', case_insensitive=True, help_command=None)

# Google Cloud DB Config
cred = credentials.Certificate("jarparur-firebase-adminsdk-wvrbl-3851eef79d.json")
firebase_admin.initialize_app(cred, {
  'projectId': 'jarparur',
})
db = firestore.client()

# Get Keys
with open("secrets.json") as s:
    dataSecrets = json.load(s)

#GLOBAL VARS
trinityRaces = ['human', 'elf']
northRaces = ['norse', 'dwarf']
independentRaces = ['woodElf', 'orc']

characterCreationDesc = """
Bem vindo ao **Jarparur**, fico feliz que tenha se interessado. Para criar um novo personagem, você precisa de uma classe e uma raça, como algumas classes são limitadas para algumas raças específicas, primeiro, preciso da raça do seu personagem.

:one: Humano
:two: Nórdico
:three: Orc
:four: Elfo
:five: Elfo da Floresta
:six: Anão
"""

verifiers = {
	'hasCatchedItem': False
}

thisCharInitials = {
	'name': None,
	'username': None,
	'level': 1,
	'xp': 0,
	'gold': 0,
	'quest': None,

	'location': None,

	'class': None,
	'race': None,
	'fight_for': None,
	'guild': None,

	'inventory': {
		'slot1': None,
		'slot2': None,
		'slot3': None,
		'slot4': None,
		'slot5': None
	},

	'health': 0,
	'armor': 0,
	'magical_resistance': 0,
	'physical_damage': 0,
	'magical_power': 0,
	'crit_chance': 0,

	'armorset': None,
	'weapon': None,

	'companion': None
}

humanCreationDesc = f"""
Sua raça será: **Humano**.

Agora, você precisa selecionar uma classe.

:one: Guerreiro
:two: Ranger
:three: Mago
:four: Paladino
:five: Clérigo
:six: Assassino
"""
elfCreationDesc = f"""
Sua raça será: **Elfo**.

Agora, você precisa selecionar uma classe.

:one: Ranger
:two: Mago
:three: Clérigo
:four: Assassino
"""
orcCreationDesc = f"""
Sua raça será: **Orc**.

Agora, você precisa selecionar uma classe.

:one: Guerreiro
:two: Bárbaro
"""
norseCreationDesc = f"""
Sua raça será: **Nórdico**.

Agora, você precisa selecionar uma classe.

:one: Guerreiro
:two: Ranger
:three: Bjoreten
:four: Bárbaro
:five: Assassino
"""
woodElfCreationDesc = f"""
Sua raça será: **Elfo da Floresta**.

Agora, você precisa selecionar uma classe.

:one: Guerreiro
:two: Ranger
:three: Assassino
"""
dwarfCreationDesc = f"""
Sua raça será: **Anão**.

Agora, você precisa selecionar uma classe.

:one: Guerreiro
:two: Bárbaro
"""

humanClasses = {
	'1️⃣': 'warrior',
	'2️⃣': 'ranger',
	'3️⃣': 'mage',
	'4️⃣': 'paladin',
	'5️⃣': 'cleric',
	'6️⃣': 'assassin'
}
elfClasses = {
	'1️⃣': 'ranger',
	'2️⃣': 'mage',
	'3️⃣': 'cleric',
	'4️⃣': 'assassin'
}
orcClasses = {
	'1️⃣': 'warrior',
	'2️⃣': 'barbarian'
}
norseClasses = {
	'1️⃣': 'warrior',
	'2️⃣': 'ranger',
	'3️⃣': 'bjoreten',
	'4️⃣': 'barbarian',
	'5️⃣': 'assassin'
}
woodElfClasses = {
	'1️⃣': 'warrior',
	'2️⃣': 'ranger',
	'3️⃣': 'assassin'
}
dwarfClasses = {
	'1️⃣': 'warrior',
	'2️⃣': 'barbarian'
}

raceReactions = {
	'1️⃣': 'human',
	'2️⃣': 'norse',
	'3️⃣': 'orc',
	'4️⃣': 'elf',
	'5️⃣': 'woodElf',
	'6️⃣': 'dwarf'
}


@client.event
async def on_reaction_add(reaction, user):
	global thisCharInitials

	if reaction.message.author.id == 858120337660968960 and user.id != 858120337660968960 and "Para criar um novo personagem, você precisa de uma classe" in reaction.message.embeds[0].description:
		thisCharInitials['race'] = raceReactions[str(reaction.emoji)]
	elif reaction.message.author.id == 858120337660968960 and user.id != 858120337660968960 and "Agora, você precisa selecionar uma classe." in reaction.message.embeds[0].description:
		if thisCharInitials['race'] == 'human':
			thisCharInitials['class'] = humanClasses[str(reaction.emoji)]
		elif thisCharInitials['race'] == 'elf':
			thisCharInitials['class'] = elfClasses[str(reaction.emoji)]
		elif thisCharInitials['race'] == 'orc':
			thisCharInitials['class'] = orcClasses[str(reaction.emoji)]
		elif thisCharInitials['race'] == 'norse':
			thisCharInitials['class'] = norseClasses[str(reaction.emoji)]
		elif thisCharInitials['race'] == 'woodElf':
			thisCharInitials['class'] = woodElfClasses[str(reaction.emoji)]
		elif thisCharInitials['race'] == 'elf':
			thisCharInitials['class'] = elfClasses[str(reaction.emoji)]
		elif thisCharInitials['race'] == 'dwarf':
			thisCharInitials['class'] = dwarfClasses[str(reaction.emoji)]
	elif reaction.message.author.id == 858120337660968960 and user.id != 858120337660968960 and "Parece que você encontrou um item!" in reaction.message.embeds[0].title:
		if reaction.emoji == "✅":
			verifiers['hasCatchedItem'] = True

@client.event
async def on_ready():
    print(f"[{datetime.today()}] {client.user.name} ligado! (id = {client.user.id})")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Contos do Bardo [build: cloud]"))
    print("======-======\n")

@client.command()
async def stats(ctx):
	statsEmbed = discord.Embed(
        title="Jarparur",
        description="by matjs#1006"
    )
	if db.collection(u'players'):
		statsEmbed.add_field(name="Dados", value=":white_check_mark:")
	else:
		statsEmbed.add_field(name="Dados", value=":no_entry_sign:")

	if firestore.client():
		statsEmbed.add_field(name="API Google Cloud", value=":white_check_mark:")
	else:
		statsEmbed.add_field(name="API Google Cloud", value=":no_entry_sign:")

	statsEmbed.add_field(name="Latência", value=f"{round(client.latency, 1)} ms", inline=False)
	statsEmbed.set_footer(text=f"Versão: {db.collection('stats').document('bot').get().get('version')}")

	await ctx.send(embed=statsEmbed)

@client.command()
async def criar(ctx, name:str=None):
	i = 10
	thisCharInitials['name'] = None
	thisCharInitials['username'] = None
	thisCharInitials['level'] = 1
	thisCharInitials['xp'] = 0
	thisCharInitials['class'] = None
	thisCharInitials['race'] = None
	thisCharInitials['fight_for'] = None
	thisCharInitials['guild'] = None
	thisCharInitials['health'] = None
	thisCharInitials['armor'] = None
	thisCharInitials['magical_resistance'] = 0
	thisCharInitials['physical_damage'] = 0
	thisCharInitials['magical_power'] = 0
	thisCharInitials['magical_resistance'] = 0
	thisCharInitials['armorset'] = None
	thisCharInitials['weapon'] = None
	thisCharInitials['companion'] = None
	thisCharInitials['crit_chance'] = 0
	thisCharInitials['location'] = None
	thisCharInitials['gold'] = 0

	alreadyHaveAChar = discord.Embed(
		title=":information_source: Você já possui um personagem!",
		description="Infelizmente, nenhum caso de múltipla personalidade foi registrado no mundo de Jarparur. Ainda."
	)

	characterCreation = discord.Embed(
		title=f":information_source: Criação do personagem {name}",
		description=characterCreationDesc
	)

	characterCreationError = discord.Embed(
		title=":information_source: Ei, todo personagem tem um nome!",
		description="Preciso que me diga o nome do personagem que deseja criar."
	)

	#Races
	humanClassSelected = discord.Embed(
		title=f":information_source: Criação do personagem {name}",
		description=humanCreationDesc
	)
	elfClassSelected = discord.Embed(
		title=f":information_source: Criação do personagem {name}",
		description=elfCreationDesc
	)
	orcClassSelected = discord.Embed(
		title=f":information_source: Criação do personagem {name}",
		description=orcCreationDesc
	)
	norseClassSelected = discord.Embed(
		title=f":information_source: Criação do personagem {name}",
		description=norseCreationDesc
	)
	woodElfClassSelected = discord.Embed(
		title=f":information_source: Criação do personagem {name}",
		description=woodElfCreationDesc
	)
	dwarfClassSelected = discord.Embed(
		title=f":information_source: Criação do personagem {name}",
		description=dwarfCreationDesc
	)

	succesfullyCreatedChar = discord.Embed(
		title=":white_check_mark: Personagem criado com sucesso!",
		description=f"""
	O personagem {name} foi inserido no mundo de Jarparur!

	O que é possível fazer no Jarparur na versão atual? (v84)

	`r?local` - Utilize para ver o local atual do seu personagem
	`r?local explorar` - Utilize para explorar o local atual. Ao explorar um local, você irá ativar eventos que pode ser bons, neutros ou ruins, tudo depende da sua sorte.
	`r?perfil` - Utilize para ver o perfil do seu personagem

	:exclamation:Atenção! => Um login seu foi criado no site oficial do BOT (jarparur.web.app), o login e senha foram enviados no seu chat privado. Aproveite! :)

	Por enquanto, isso é Jarparur, mas logo o BOT irá receber novas atualizações e o mundo do jogo irá se expandir, até lá, explore muitas regiões e junte muito ouro, pois novos eventos globais virão e com eles, desafios impressionantes.
	"""
	)

	if name == None:
		await ctx.send(embed=characterCreationError)
		return
	if db.collection('players').document(str(ctx.author.id)).get().get('name') != None:
		await ctx.send(embed=alreadyHaveAChar)
		return

	thisMsg = await ctx.send(embed=characterCreation)
	await thisMsg.add_reaction('1️⃣')
	await thisMsg.add_reaction('2️⃣')
	await thisMsg.add_reaction('3️⃣')
	await thisMsg.add_reaction('4️⃣')
	await thisMsg.add_reaction('5️⃣')
	await thisMsg.add_reaction('6️⃣')

	# Espera o jogador selecionar a raça
	while True:
		characterCreation.set_footer(text=f"{str(i)} segundos para cancelar.")
		await thisMsg.edit(embed=characterCreation)

		if i > 0:
			if thisCharInitials['race'] != None:
				break
		else:
			await thisMsg.delete()
			return

		time.sleep(1)
		i -= 1

	getRace = {
		"human": humanClassSelected,
		"elf": elfClassSelected,
		"orc": orcClassSelected,
		"woodElf": woodElfClassSelected,
		"norse": norseClassSelected,
		"dwarf": dwarfClassSelected
	}

	# Limpa reações e adiciona as novas
	await thisMsg.clear_reactions()

	await thisMsg.edit(embed=getRace[thisCharInitials['race']])
	if thisCharInitials['race'] == 'human':
		await thisMsg.add_reaction('1️⃣')
		await thisMsg.add_reaction('2️⃣')
		await thisMsg.add_reaction('3️⃣')
		await thisMsg.add_reaction('4️⃣')
		await thisMsg.add_reaction('5️⃣')
		await thisMsg.add_reaction('6️⃣')
	elif thisCharInitials['race'] == 'elf':
		await thisMsg.add_reaction('1️⃣')
		await thisMsg.add_reaction('2️⃣')
		await thisMsg.add_reaction('3️⃣')
		await thisMsg.add_reaction('4️⃣')
	elif thisCharInitials['race'] == 'orc':
		await thisMsg.add_reaction('1️⃣')
		await thisMsg.add_reaction('2️⃣')
	elif thisCharInitials['race'] == 'norse':
		await thisMsg.add_reaction('1️⃣')
		await thisMsg.add_reaction('2️⃣')
		await thisMsg.add_reaction('3️⃣')
		await thisMsg.add_reaction('4️⃣')
		await thisMsg.add_reaction('5️⃣')
	elif thisCharInitials['race'] == 'woodElf':
		await thisMsg.add_reaction('1️⃣')
		await thisMsg.add_reaction('2️⃣')
		await thisMsg.add_reaction('3️⃣')
	elif thisCharInitials['race'] == 'dwarf':
		await thisMsg.add_reaction('1️⃣')
		await thisMsg.add_reaction('2️⃣')

	# Espera o jogador selecionar a classe
	i = 10
	while True:
		getRace[thisCharInitials['race']].set_footer(text=f"{str(i)} segundos para cancelar.")
		await thisMsg.edit(embed=getRace[thisCharInitials['race']])

		if i > 0:
			if thisCharInitials['class'] != None:
				break
		else:
			await thisMsg.delete()
			return

		time.sleep(1)
		i -= 1

	# Definição de atributos iniciais dependendo da classe selecionada
	# Vida = (Armor+1)*(MR+1)*level

	classRef = db.collection('classes')
	itemRef = db.collection('items')
	thisPlayerClass = thisCharInitials['class']

	thisCharInitials['name'] = name
	thisCharInitials['username'] = str(ctx.author)
	
	if thisCharInitials['race'] in trinityRaces:
		thisCharInitials['fight_for'] = "trinity"
	elif thisCharInitials['race'] in northRaces:
		thisCharInitials['fight_for'] = "winterBrigade"
	else:
		thisCharInitials['fight_for'] = "independent"

	thisCharInitials['armorset'] = classRef.document(thisPlayerClass).get().get('starter_armorset')
	thisCharInitials['weapon'] = classRef.document(thisPlayerClass).get().get('starter_weapon')


	thisCharInitials['armor'] = classRef.document(thisPlayerClass).get().get('base_armor') + itemRef.document(thisCharInitials['armorset']).get().get('armor') + itemRef.document(thisCharInitials['weapon']).get().get('armor')

	thisCharInitials['magical_resistance'] = classRef.document(thisPlayerClass).get().get('base_magical_resistance') + itemRef.document(thisCharInitials['armorset']).get().get('magical_resistance') + itemRef.document(thisCharInitials['weapon']).get().get('magical_resistance')

	thisCharInitials['physical_damage'] = classRef.document(thisPlayerClass).get().get('base_physical_damage') +  itemRef.document(thisCharInitials['armorset']).get().get('physical_damage') +  itemRef.document(thisCharInitials['weapon']).get().get('physical_damage')

	thisCharInitials['magical_power'] = classRef.document(thisPlayerClass).get().get('base_magical_power') + itemRef.document(thisCharInitials['armorset']).get().get('magical_power') + itemRef.document(thisCharInitials['weapon']).get().get('magical_power') 

	thisCharInitials['crit_chance'] = classRef.document(thisPlayerClass).get().get('crit_chance')


	thisCharInitials['health'] = (thisCharInitials['armor']+1)*(thisCharInitials['magical_resistance']+1)*thisCharInitials['level']

	if thisCharInitials['fight_for'] == "trinity":
		thisCharInitials['location'] = "lightBastion"
	elif thisCharInitials['fight_for'] == "winterBrigade":
		thisCharInitials['location'] = "nulrbrakk"
	elif thisCharInitials['race'] == "woodElf":
		thisCharInitials['location'] = "sentinelEmpire"
	elif thisCharInitials['race'] == "orc":
		thisCharInitials['location'] = "ukshala"

	if thisCharInitials['class'] == "ranger":
		thisCharInitials['companion'] = 'wolfCompanion'

	first = [""]

	lower = string.ascii_lowercase
	upper = string.ascii_uppercase
	num = string.digits
	allPoss = string.ascii_letters + string.digits

	loginData = {
		'user': str(ctx.author),
		'id': str(ctx.author.id),
		'password': ''.join(random.sample(allPoss,10)),
		'avatar': str(ctx.author.avatar)
	}

	user = ctx.author

	accountDesc = f"""
	Sua conta foi criada com sucesso, só estou aqui para te agradecer e claro, te mandar suas credenciais de login no site do Jarparur.

	**Login**: {loginData['user']}
	**Senha**: {loginData['password']}
	"""

	yourAccount = discord.Embed(
		title=":white_check_mark: Perfil criado com sucesso!",
		description=accountDesc
	)

	db.collection('players').document(str(ctx.author.id)).set(thisCharInitials)
	db.collection('users').document(str(ctx.author.id)).set(loginData)

	await thisMsg.edit(embed=succesfullyCreatedChar)
	await user.send(embed=yourAccount)
	await thisMsg.clear_reactions()

@client.command()
async def perfil(ctx, user: discord.User=None):
	dbRef = db.collection('players')
	dbRefItems = db.collection('items')
	dbRefGuilds = db.collection('guilds')
	dbRefFactions = db.collection('factions')
	dbRefPets = db.collection('companions')
	dbRefRaces = db.collection('races')
	dbRefClasses = db.collection('classes')

	doestHaveAccount = discord.Embed(
		title=":information_source: Você ainda não criou um personagem",
		description="Utilize o comando `r?criar [nome do personagem]` para criar seu persoangem!"
	)

	if user == None:
		thisPlayerDoc = dbRef.document(str(ctx.author.id))
	else:
		thisPlayerDoc = dbRef.document(str(user.id))

	if thisPlayerDoc.get().get('name') == None:
		await ctx.send(embed=doestHaveAccount)
		return

	titleDict = {
		'warrior': ':crossed_swords:',
		'ranger': ':bow_and_arrow:',
		'barbarian': ':axe:',
		'paladin': ':shield:',
		'cleric': 'shield',
		'mage': ':mage:',
		'bjoreten': ':herb:',
		'assassin': ':dagger:'
	}

	thisPlayerEmbed = discord.Embed(
		title=f"{thisPlayerDoc.get().get('name')} {titleDict[thisPlayerDoc.get().get('class')]}",
		description=f"{dbRefRaces.document(thisPlayerDoc.get().get('race')).get().get('name')} {dbRefClasses.document(thisPlayerDoc.get().get('class')).get().get('name')}, Nível {thisPlayerDoc.get().get('level')} ({thisPlayerDoc.get().get('xp')} XP)."
	)
	thisPlayerEmbed.add_field(name="Lado da guerra", value=f"{dbRefFactions.document(thisPlayerDoc.get().get('fight_for')).get().get('name')}", inline=True)
	if thisPlayerDoc.get().get('guild') == None:
		thisPlayerEmbed.add_field(name="Guilda", value=f"Nenhuma")
	else:
		thisPlayerEmbed.add_field(name="Guilda", value=f"{dbRefGuilds.document(thisPlayerDoc.get().get('guild')).get().get('name')}")
	thisPlayerEmbed.add_field(name="Moedas de Ouro :coin:", value=thisPlayerDoc.get().get('gold'))
	if thisPlayerDoc.get().get('quest') == None:
		thisPlayerEmbed.add_field(name="Quest Atual", value="Nenhuma")
	else:
		thisPlayerEmbed.add_field(name="Quest Atual", value=thisPlayerDoc.get().get('quest'))

	thisPlayerEmbed.add_field(name="Pontos de Vida :drop_of_blood:", value=f"{thisPlayerDoc.get().get('health')}/{(dbRef.document(str(ctx.author.id)).get().get('armor')+1) * (dbRef.document(str(ctx.author.id)).get().get('magical_resistance')+1) * dbRef.document(str(ctx.author.id)).get().get('level')}", inline=False)
	thisPlayerEmbed.add_field(name="Armadura :shield:", value=f"{thisPlayerDoc.get().get('armor')}", inline=False)
	thisPlayerEmbed.add_field(name="Resistência Mágica :shield:", value=f"{thisPlayerDoc.get().get('magical_resistance')}", inline=False)
	thisPlayerEmbed.add_field(name="Dano Físico :crossed_swords:", value=f"{thisPlayerDoc.get().get('physical_damage')}", inline=False)
	thisPlayerEmbed.add_field(name="Dano Mágico :sparkles:", value=f"{thisPlayerDoc.get().get('magical_power')}", inline=False)
	thisPlayerEmbed.add_field(name="Chance de Crítico :zap:", value=f"{thisPlayerDoc.get().get('crit_chance')}%", inline=False)

	thisPlayerEmbed.add_field(name="Traje", value=f"{dbRefItems.document(thisPlayerDoc.get().get('armorset')).get().get('name')}", inline=True)
	thisPlayerEmbed.add_field(name="Arma", value=f"{dbRefItems.document(thisPlayerDoc.get().get('weapon')).get().get('name')}")

	if thisPlayerDoc.get().get('companion') == None:
		thisPlayerEmbed.add_field(name="Pet", value="Nenhum", inline=False)
	else:
		dbRefCompanions = db.collection('companions')
		thisPlayerEmbed.add_field(name="Pet", value=f"{dbRefPets.document(thisPlayerDoc.get().get('companion')).get().get('name')} (+{dbRefCompanions.document(dbRef.document(str(ctx.author.id)).get().get('companion')).get().get('physical_damage')} Dano Físico | +{dbRefCompanions.document(dbRef.document(str(ctx.author.id)).get().get('companion')).get().get('magical_power')} Dano Mágico)", inline=False)

	thisPlayerEmbed.set_footer(text="Utilize `r?inv` para ser seu invetário")

	await ctx.send(embed=thisPlayerEmbed)

@client.command()
async def inv(ctx, action: str=None, arg: str=None):
	dbRef = db.collection('players')
	dbRefItems = db.collection('items')
	dbRefGuilds = db.collection('guilds')
	dbRefFactions = db.collection('factions')
	dbRefPets = db.collection('companions')
	dbRefRaces = db.collection('races')
	dbRefClasses = db.collection('classes')

	doestHaveAccount = discord.Embed(
		title=":information_source: Você ainda não criou um personagem",
		description="Utilize o comando `r?criar [nome do personagem]` para criar seu persoangem!"
	)

	thisPlayerDoc = dbRef.document(str(ctx.author.id))

	if thisPlayerDoc.get().get('name') == None:
		await ctx.send(embed=doestHaveAccount)
		return

	itemsDict = {
		'armorset': ':shield:',
		'weapon': ':crossed_swords:',
		'lifePotion': ':drop_of_blood:',
		'physDamBuff': ':muscle:'
	}

	# if thisItemType == "weapon":
	# 	actualWeapon = dbRef.document(str(ctx.author.id)).get().get('weapon')

	# 	dbRef.document(str(ctx.author.id)).update({
	# 		'physical_damage': (dbRef.document(str(ctx.author.id)).get().get('physical_damage') - dbRefItems.document(actualWeapon).get().get('physical_damage')) + dbRefItems.document(commandShop[acao2]).get().get('physical_damage'),
	# 		'magical_power': (dbRef.document(str(ctx.author.id)).get().get('magical_power') - dbRefItems.document(actualWeapon).get().get('magical_power')) + dbRefItems.document(commandShop[acao2]).get().get('magical_power'),
	# 		'weapon': thisItemID
	# 	})
	# elif thisItemType == "armorset":
	# 	actualArmorset = dbRef.document(str(ctx.author.id)).get().get('armorset')

	# 	dbRef.document(str(ctx.author.id)).update({
	# 		'armor': (dbRef.document(str(ctx.author.id)).get().get('armor') - dbRefItems.document(actualArmorset).get().get('armor')) + dbRefItems.document(commandShop[acao2]).get().get('armor'),
	# 		'magical_resistance': (dbRef.document(str(ctx.author.id)).get().get('magical_resistance') - dbRefItems.document(actualArmorset).get().get('magical_resistance')) + dbRefItems.document(commandShop[acao2]).get().get('magical_resistance'),
	# 		'armorset': thisItemID
	# 	})

	# 	dbRef.document(str(ctx.author.id)).update({
	# 		'health': (dbRef.document(str(ctx.author.id)).get().get('armor')+1) * (dbRef.document(str(ctx.author.id)).get().get('magical_resistance')+1) * dbRef.document(str(ctx.author.id)).get().get('level')
	# 	})
	# elif thisItemType == "lifePotion":
	# 	howMuch =  dbRefItems.document(commandShop[acao2]).get().get('howMuch')
	# 	maxLife = (dbRef.document(str(ctx.author.id)).get().get('armor')+1) * (dbRef.document(str(ctx.author.id)).get().get('magical_resistance')+1) * dbRef.document(str(ctx.author.id)).get().get('level')

	# 	lifeFull = discord.Embed(
	# 		title=":information_source: Seus pontos de vida estão cheios!",
	# 		description="Não há necessidade de comprar este item."
	# 	)

	# 	if dbRef.document(str(ctx.author.id)).get().get('health') == maxLife:
	# 		await ctx.send(embed=lifeFull)
	# 		return
	# 	else:
	# 		# TO DO
	# 		# Adicionar n pontos de vida até que chegue ao máximo
	# 		howMuchRecovered = 0
	# 		for i in range(0, howMuch):
	# 			if dbRef.document(str(ctx.author.id)).get().get('health') == maxLife:
	# 				break
	# 			else: 
	# 				dbRef.document(str(ctx.author.id)).update({
	# 					'health': dbRef.document(str(ctx.author.id)).get().get('health') + 1
	# 				})
	# 				howMuchRecovered += 1
					
	# 		if howMuchRecovered > 1:
	# 			lifeRecovered = discord.Embed(
	# 				title=f":white_check_mark: Seus pontos de vida foram recuperados! (-{thisItemPrice} moedas de ouro)",
	# 				description=f"Você recuperou {howMuchRecovered} pontos de vida."
	# 			)
	# 		else:
	# 			lifeRecovered = discord.Embed(
	# 				title=f":white_check_mark: Seus pontos de vida foram recuperados! (-{thisItemPrice} moedas de ouro)",
	# 				description=f"Você recuperou {howMuchRecovered} ponto de vida."
	# 			)

	# 		await ctx.send(embed=lifeRecovered)
	# 		return

	inventoryEmbed = discord.Embed(
		title=f"Inventário de {thisPlayerDoc.get().get('name')}",
		description=""
	)

	succesfullyRemoved = discord.Embed(
		title=":white_check_mark: Item removido com sucesso!"
	)

	needArg = discord.Embed(
		title=":information_source: Você precisa informar qual slot deseja descartar",
	)

	if action == None:
		for item in thisPlayerDoc.get().get('inventory'):
			if thisPlayerDoc.get().get('inventory')[item] == None:
				inventoryEmbed.add_field(name=f"{item}", value="Nenhum item", inline=False)
			else:
				inventoryEmbed.add_field(name=f"{item}", value=f"{itemsDict[dbRefItems.document(thisPlayerDoc.get().get('inventory')[item]).get().get('type')]} {dbRefItems.document(thisPlayerDoc.get().get('inventory')[item]).get().get('name')}", inline=False)

		inventoryEmbed.add_field(name="Traje", value=dbRefItems.document(thisPlayerDoc.get().get('armorset')).get().get('name'))
		inventoryEmbed.add_field(name="Arma Equipada", value=dbRefItems.document(thisPlayerDoc.get().get('weapon')).get().get('name'))
		await ctx.send(embed=inventoryEmbed)
	elif action == "d":
		if arg == None:
			await ctx.send(embed=needArg)
		else:
			newInv = {}

			for slot in thisPlayerDoc.get().get('inventory'):
				if slot == arg or slot[-1] == arg:
					newInv[slot] = None
				else:
					newInv[slot] = dbRef.document(str(ctx.author.id)).get().get('inventory')[slot]
			
			dbRef.document(str(ctx.author.id)).update({
				'inventory': newInv
			})

			await ctx.send(embed=succesfullyRemoved)
	elif "slot" in action:
		for slot in thisPlayerDoc.get().get('inventory'):
			if slot == action:
				if dbRefItems.document(thisPlayerDoc.get().get('inventory')[slot]).get().get('name') == None:
					thisItem = discord.Embed(
						title = "Nenhum item"
					)
				else:
					thisItem = discord.Embed(
						title = f"{itemsDict[dbRefItems.document(thisPlayerDoc.get().get('inventory')[slot]).get().get('type')]} {dbRefItems.document(thisPlayerDoc.get().get('inventory')[slot]).get().get('name')}",
						description = dbRefItems.document(thisPlayerDoc.get().get('inventory')[slot]).get().get('description')
					)
					if dbRefItems.document(thisPlayerDoc.get().get('inventory')[slot]).get().get('type') == "armorset":
						thisItem.add_field(name="Armadura", value=dbRefItems.document(thisPlayerDoc.get().get('inventory')[slot]).get().get('armor'))
						thisItem.add_field(name="Resistência Mágica", value=dbRefItems.document(thisPlayerDoc.get().get('inventory')[slot]).get().get('magical_resistance'))
					elif dbRefItems.document(thisPlayerDoc.get().get('inventory')[slot]).get().get('type') == "weapon":
						thisItem.add_field(name="Dano Físico", value=dbRefItems.document(thisPlayerDoc.get().get('inventory')[slot]).get().get('physical_damage'))
						thisItem.add_field(name="Dano Mágico", value=dbRefItems.document(thisPlayerDoc.get().get('inventory')[slot]).get().get('magical_power'))
					elif dbRefItems.document(thisPlayerDoc.get().get('inventory')[slot]).get().get('type') == "lifePotion":
						thisItem.add_field(name="Regenera", value=f"{dbRefItems.document(thisPlayerDoc.get().get('inventory')[slot]).get().get('howMuch')} pontos de vida")
					elif dbRefItems.document(thisPlayerDoc.get().get('inventory')[slot]).get().get('type') == "physDamBuff":
						thisItem.add_field(name="Adiciona", value=f"{dbRefItems.document(thisPlayerDoc.get().get('inventory')[slot]).get().get('howMuch')} de dano físico")
				
				await ctx.send(embed=thisItem)


@client.command()
async def local(ctx, acao: str=None, interacao: str=None, acao2: str=None):
	dbRef = db.collection('players')
	dbRefLocals = db.collection('locations')
	dbRefFactions = db.collection('factions')
	dbRefItems = db.collection('items')

	verifiers['hasCatchedItem'] = False

	i = 0

	formattedActions = []
	commandActions = {}
	commandShop = {}

	interactionNotFound = discord.Embed(
		title=":information_source: Algo deu errado!",
		description="Parece que a ação que você inseriu não existe. Tente usar `r?local` para ver oque você pode fazer por aqui."
	)

	# Local atual
	for action in dbRefLocals.document(dbRef.document(str(ctx.author.id)).get().get('location')).get().get('actions'):
		formattedActions.append(f'`r?local {i}` para interagir | {dbRefLocals.document(action).get().get("name")}')
		commandActions[str(i)] = action
		i += 1
	formattedActions.append(f'`r?local explorar` para ver oque você pode encontrar por aqui.')

	if acao == None:
		# Preparando interface do local atual
		thisLocalEmbed = discord.Embed(
			title=f"Você está em: {dbRefLocals.document(dbRef.document(str(ctx.author.id)).get().get('location')).get().get('name')}",
			description=f"{dbRefLocals.document(dbRef.document(str(ctx.author.id)).get().get('location')).get().get('description')}"
		)
		thisLocalEmbed.set_image(url=dbRefLocals.document(dbRef.document(str(ctx.author.id)).get().get('location')).get().get('img'))

		thisLocalEmbed.add_field(name="O que há por aqui", value="\n".join(formattedActions))

		await ctx.send(embed=thisLocalEmbed)

	# Ações no local atual
	elif acao in commandActions:
		# Preparando variáveis da loja
		if dbRefLocals.document(commandActions[acao]).get().get('type') == "shop":
			# Preparando a interface da loja
			thisActionEmbed = discord.Embed(
				title=f"{dbRefLocals.document(commandActions[acao]).get().get('name')}",
				description=f"{dbRefLocals.document(commandActions[acao]).get().get('description')}"
			)
			thisActionEmbed.set_image(url=dbRefLocals.document(commandActions[acao]).get().get('img'))

			i = 0
			for item in dbRefLocals.document(commandActions[acao]).get().get('items'):
				thisActionEmbed.add_field(name=dbRefItems.document(item).get().get('name'), value=f'`r?local {acao} comprar {i}` | Preço: {dbRefItems.document(item).get().get("price")}', inline=False)
				commandShop[str(i)] = item
				i += 1

			# Comprando um item da loja
			if interacao == "comprar":
				if acao2 in commandShop:
					thisPlayerGold = dbRef.document(str(ctx.author.id)).get().get('gold')
					thisItemPrice = dbRefItems.document(commandShop[acao2]).get().get('price')
					thisItemName = dbRefItems.document(commandShop[acao2]).get().get('name')
					thisItemType = dbRefItems.document(commandShop[acao2]).get().get('type')
					thisItemID = dbRefItems.document(commandShop[acao2]).id

					if thisPlayerGold >= thisItemPrice:
						# TO DO
						# Hidromel e outros itens do tipo "buff"

						succesfullyPurchased = discord.Embed(
							title=f":white_check_mark: Você comprou o item '{thisItemName}'! (-{thisItemPrice} moedas de ouro)",
							description=f"O item '{thisItemName}' foi adicionado ao seu inventário."
						)

						notEnoughSpace = discord.Embed(
							title=f":information_source: Sem espaço no inventário",
							description="Parece que você não possui espaço o suficiente no seu inventário para comprar este item. Utilize o comando `r?inv d [slot]` para descartar um item."
						)
						
						dbRef.document(str(ctx.author.id)).update({
							'gold': thisPlayerGold - thisItemPrice
						})

						newInv = {}
						hasAdded = False

						for slot in dbRef.document(str(ctx.author.id)).get().get('inventory'):
							if dbRef.document(str(ctx.author.id)).get().get('inventory')[slot] == None:
								if hasAdded == True:
									newInv[slot] = None
								else:
									newInv[slot] = thisItemID
									hasAdded = True
							else:
								newInv[slot] = dbRef.document(str(ctx.author.id)).get().get('inventory')[slot]

						if hasAdded == False:
							await ctx.send(embed=notEnoughSpace)
							return

						dbRef.document(str(ctx.author.id)).update({
							'inventory': newInv
						})

						if thisItemType == None:
							await ctx.send("Opa! Parece que você encontrou um item em desenvolvimento, bem, isso não deveria acontecer. Meus parabéns!")
							return
						
						await ctx.send(embed=succesfullyPurchased)
					else:
						await ctx.send(f"Não pode comprar => você tem {thisPlayerGold} moedas de ouro e o item custa {thisItemPrice} moedas de ouro.")
					return

			elif interacao == "vender":
				newInv = {}

				if "slot" in acao2:
					for slot in dbRef.document(str(ctx.author.id)).get().get('inventory'):
						if slot == acao2:
							succesfullySold = discord.Embed(
								title=f":white_check_mark: Você vendeu o item {dbRefItems.document(dbRef.document(str(ctx.author.id)).get().get('inventory')[acao2]).get().get('name')} por {dbRefItems.document(dbRef.document(str(ctx.author.id)).get().get('inventory')[acao2]).get().get('price')} moedas de ouro!"
							)
							newInv[slot] = None
						else:
							newInv[slot] = dbRef.document(str(ctx.author.id)).get().get('inventory')[slot]

					dbRef.document(str(ctx.author.id)).update({
						'inventory': newInv,
						'gold':  dbRef.document(str(ctx.author.id)).get().get('gold') + dbRefItems.document(dbRef.document(str(ctx.author.id)).get().get('inventory')[acao2]).get().get('price')
					})

					await ctx.send(embed=succesfullySold)
					return

			await ctx.send(embed=thisActionEmbed)

	elif acao == "explorar":
		# Ainda em desenvolvimento.
		# await ctx.send("Este comando irá servir para explorar o local atual, seja um reino, vijarejo ou outros ambientes como uma floresta, uma espécie de 'loot', porém mais detalhado.")
		events = ['bad', 'neutral', 'good']
		choosedOne = random.choice(events)

		if choosedOne == "bad":
			badEvents = db.collection("events").where("type", "==", "bad")
			thisEvent = random.choice(badEvents.get())

			thisEventEmbed = discord.Embed(
				title=f"{thisEvent.get('name')}",
				description=f"{thisEvent.get('description')}"
			)
			thisEventEmbed.set_author(name=ctx.author)

			if thisEvent.get('combat') == None:
				dbRef.document(str(ctx.author.id)).update({
					'gold': dbRef.document(str(ctx.author.id)).get().get('gold') - thisEvent.get('gold'),
					'xp': dbRef.document(str(ctx.author.id)).get().get('xp') - thisEvent.get('xp')
				})
			else:
				thisMsg = await ctx.send(embed=thisEventEmbed)

				i = 10
				while True:
					thisEventEmbed.set_footer(text=f"{i} segundos para começar o combate")
					await thisMsg.edit(embed=thisEventEmbed)
					time.sleep(1)
					if i > 0:
						i -= 1
					else:
						await thisMsg.delete()
						break
				
				# Combate
				dbRefCreatures = db.collection('creatures')
				dbRefCompanions = db.collection('companions')

				enemyID = thisEvent.get('combat')

				playerState = "Atacando"
				enemyState = "Defendendo"

				if dbRef.document(str(ctx.author.id)).get().get('companion') != None:
					playerAD = dbRef.document(str(ctx.author.id)).get().get('physical_damage') + dbRefCompanions.document(dbRef.document(str(ctx.author.id)).get().get('companion')).get().get('physical_damage')
					playerMP = dbRef.document(str(ctx.author.id)).get().get('magical_power') + dbRefCompanions.document(dbRef.document(str(ctx.author.id)).get().get('companion')).get().get('magical_power')
				else:
					playerAD = dbRef.document(str(ctx.author.id)).get().get('physical_damage')
					playerMP = dbRef.document(str(ctx.author.id)).get().get('magical_power')
				enemyAD = dbRefCreatures.document(enemyID).get().get('physical_damage')
				enemyMP = dbRefCreatures.document(enemyID).get().get('magical_power')

				playerAR = dbRef.document(str(ctx.author.id)).get().get('armor')
				playerMR = dbRef.document(str(ctx.author.id)).get().get('magical_resistance')
				enemyAR = dbRefCreatures.document(enemyID).get().get('armor')
				enemyMR = dbRefCreatures.document(enemyID).get().get('magical_resistance')

				if playerMP != 0:
					for i in range(0, enemyMR):
						if playerMP == 0:
							break
						playerMP -= 1
				if playerAD != 0:
					for i in range(0, enemyAR):
						if playerAD == 0:
							break
						playerAD -= 1

				if enemyMP != 0:
					for i in range(0, playerMR):
						if enemyMP == 0:
							break
						enemyMP -= 1
				if enemyAD != 0:
					for i in range(0, playerAR):
						if enemyAD == 0:
							break
						enemyAD -= 1

				playerTotalDamage = playerAD + playerMP
				enemyTotalDamage = enemyAD + enemyMP

				playerWon = discord.Embed(
					title=f":crossed_swords: :white_check_mark: Você ganhou!",
					description=f"Você derrotou '{dbRefCreatures.document(enemyID).get().get('name')}' e ganhou {dbRefCreatures.document(enemyID).get().get('xp')} de XP!"
				)

				playerLose = discord.Embed(
					title=f":crossed_swords: :x: Você perdeu!",
					description=f"O inimigo '{dbRefCreatures.document(enemyID).get().get('name')}' te derrotou, você perdeu {dbRefCreatures.document(enemyID).get().get('gold')} moedas de ouro."
				)

				playerPreviousXP = dbRef.document(str(ctx.author.id)).get().get('xp')
				leveledUp = False

				thisEnemyHealth = dbRefCreatures.document(enemyID).get().get('health')
				thisPlayerHealth = dbRef.document(str(ctx.author.id)).get().get('health')

				playerCard = discord.Embed(
					title=f"{dbRef.document(str(ctx.author.id)).get().get('name')} ({playerState})"
				)
				playerCard.add_field(name="Pontos de Vida", value=f"{dbRef.document(str(ctx.author.id)).get().get('health')}/{(dbRef.document(str(ctx.author.id)).get().get('armor')+1) * (dbRef.document(str(ctx.author.id)).get().get('magical_resistance')+1) * dbRef.document(str(ctx.author.id)).get().get('level')}")
				playerCard.add_field(name="Dano Causado", value=0)
				playerCard.add_field(name="Dano Recebido", value=0)

				enemyCard = discord.Embed(
					title=f"{dbRefCreatures.document(enemyID).get().get('name')} ({enemyState})",
				)
				enemyCard.add_field(name="Pontos de Vida", value=f"{dbRefCreatures.document(enemyID).get().get('health')}/{(dbRefCreatures.document(enemyID).get().get('armor')+1)*(dbRefCreatures.document(enemyID).get().get('magical_resistance')+1)*dbRefCreatures.document(enemyID).get().get('difficulty')}")
				enemyCard.add_field(name="Dano Causado", value=0)
				enemyCard.add_field(name="Dano Recebido", value=0)

				thisPlayerMsg = await ctx.send(embed=playerCard)
				thisEnemyMsg = await ctx.send(embed=enemyCard)

				while True:
					if playerState == "Atacando":
						if thisEnemyHealth <= 0:
							dbRef.document(str(ctx.author.id)).update({
								'gold': dbRef.document(str(ctx.author.id)).get().get('gold') + dbRefCreatures.document(enemyID).get().get('gold'),
								'xp': dbRef.document(str(ctx.author.id)).get().get('xp') + dbRefCreatures.document(enemyID).get().get('xp')
							})

							if dbRef.document(str(ctx.author.id)).get().get('xp') >= 100 and playerPreviousXP <= 100:
								dbRef.document(str(ctx.author.id)).update({
									'level': 2
								})
								leveledUp = True
							elif dbRef.document(str(ctx.author.id)).get().get('xp') >= 500 and playerPreviousXP <= 500:
								dbRef.document(str(ctx.author.id)).update({
									'level': 3
								})
								leveledUp = True
							elif dbRef.document(str(ctx.author.id)).get().get('xp') >= 1000 and playerPreviousXP <= 1000:
								dbRef.document(str(ctx.author.id)).update({
									'level': 4
								})
								leveledUp = True
							elif dbRef.document(str(ctx.author.id)).get().get('xp') >= 1500 and playerPreviousXP <= 1500:
								dbRef.document(str(ctx.author.id)).update({
									'level': 5
								})
								leveledUp = True
							elif dbRef.document(str(ctx.author.id)).get().get('xp') >= 2500 and playerPreviousXP <= 2500:
								dbRef.document(str(ctx.author.id)).update({
									'level': 6
								})
								leveledUp = True
							elif dbRef.document(str(ctx.author.id)).get().get('xp') >= 3500 and playerPreviousXP <= 3500:
								dbRef.document(str(ctx.author.id)).update({
									'level': 7
								})
								leveledUp = True
							elif dbRef.document(str(ctx.author.id)).get().get('xp') >= 4500 and playerPreviousXP <= 4500:
								dbRef.document(str(ctx.author.id)).update({
									'level': 8
								})
								leveledUp = True
							elif dbRef.document(str(ctx.author.id)).get().get('xp') >= 5500 and playerPreviousXP <= 5500:
								dbRef.document(str(ctx.author.id)).update({
									'level': 9
								})
								leveledUp = True
							elif dbRef.document(str(ctx.author.id)).get().get('xp') >= 6500 and playerPreviousXP <= 6500:
								dbRef.document(str(ctx.author.id)).update({
									'level': 10
								})
								leveledUp = True
							
							if leveledUp == True:
								levelUP = discord.Embed(
									title=":partying_face: Você subiu de nível!",
									description=f"Parabéns! Você avançou para o nível {dbRef.document(str(ctx.author.id)).get().get('level')}"
								)

								await ctx.send(embed=levelUP)

							await ctx.send(embed=playerWon)

							if dbRefCreatures.document(enemyID).get().get('loot') != None:
								thisItemFormated = dbRefCreatures.document(enemyID).get().get('loot')
								thisItemName = dbRefItems.document(thisItemFormated).get().get('name')
								thisItemDescription = dbRefItems.document(thisItemFormated).get().get('description')
								thisItemType = dbRefItems.document(thisItemFormated).get().get('type')
								

								thisItemEmbed = discord.Embed(
									title=f"Parece que você encontrou um item! => {thisItemName}",
									description=f"{thisItemDescription}"
								)
								if thisItemType == "armorset":
									thisItemEmbed.add_field(name="Armadura :shield:", value=dbRefItems.document(thisItemFormated).get().get('armor'))
									thisItemEmbed.add_field(name="Resistência Mágica :shield", value=dbRefItems.document(thisItemFormated).get().get('magical_resistence'))
								elif thisItemType == "weapon":
									thisItemEmbed.add_field(name="Dano Físico :crossed_swords:", value=dbRefItems.document(thisItemFormated).get().get('physical_damage'))
									thisItemEmbed.add_field(name="Dano Mágico :sparkles:", value=dbRefItems.document(thisItemFormated).get().get('magical_power'))

								thisMsg = await ctx.send(embed=thisItemEmbed)
								await thisMsg.add_reaction('✅')

								i=10
								while True:
									thisItemEmbed.set_footer(text=f"Reaja ao ✅ para receber o item. | {i} segundos restantes")
									await thisMsg.edit(embed=thisItemEmbed)
									if i > 0:
										if verifiers['hasCatchedItem'] == True:
											break
									else:
										await thisMsg.delete()
										return

									time.sleep(1)
									i -= 1

								succesfullyAddedItem = discord.Embed(
									title=":white_check_mark: Item adicionado ao inventário",
									description=f"O item '{thisItemName}' foi adicionado ao seu inventário."
								)

								if thisItemType == "weapon":
									prev = dbRef.document(str(ctx.author.id)).get().get('weapon')

									dbRef.document(str(ctx.author.id)).update({
										'physical_damage': (dbRef.document(str(ctx.author.id)).get().get('physical_damage') - dbRefItems.document(prev).get().get('physical_damage')) + dbRefItems.document(thisItemFormated).get().get('physical_damage'),
										'magical_power': (dbRef.document(str(ctx.author.id)).get().get('magical_power') - dbRefItems.document(prev).get().get('magical_power')) + dbRefItems.document(thisItemFormated).get().get('magical_power'),
										'weapon': dbRefItems.document(thisItemFormated).id
									})
								elif thisItemType == "armorset":
									prev = dbRef.document(str(ctx.author.id)).get().get('armorset')
									
									dbRef.document(str(ctx.author.id)).update({
										'armor': (dbRef.document(str(ctx.author.id)).get().get('armor') - dbRefItems.document(prev).get().get('armor')) + dbRefItems.document(thisItemFormated).get().get('armor'),
										'physical_damage': (dbRef.document(str(ctx.author.id)).get().get('physical_damage') - dbRefItems.document(prev).get().get('physical_damage')) + dbRefItems.document(thisItemFormated).get().get('physical_damage'),
										'armorset': dbRefItems.document(thisItemFormated).id
									})

								await ctx.send(embed=succesfullyAddedItem)

							return
						else:
							playerCrited = False
							if random.randint(0, 100) <= dbRef.document(str(ctx.author.id)).get().get('crit_chance'):
								playerTotalDamage += playerTotalDamage
								playerCrited = True
							thisEnemyHealth -= playerTotalDamage

							newEnemyCard = discord.Embed(
								title=f"{dbRefCreatures.document(enemyID).get().get('name')} ({enemyState})",
							)
							newEnemyCard.add_field(name="Pontos de Vida", value=f"{thisEnemyHealth}/{(dbRefCreatures.document(enemyID).get().get('armor')+1)*(dbRefCreatures.document(enemyID).get().get('magical_resistance')+1)*dbRefCreatures.document(enemyID).get().get('difficulty')}")
							newEnemyCard.add_field(name="Dano Causado", value=0)
							newEnemyCard.add_field(name="Dano Recebido", value=playerTotalDamage)

							newPlayerCard = discord.Embed(
								title=f"{dbRef.document(str(ctx.author.id)).get().get('name')} ({playerState})",
							)
							newPlayerCard.add_field(name="Pontos de Vida", value=f"{thisPlayerHealth}/{(dbRef.document(str(ctx.author.id)).get().get('armor')+1) * (dbRef.document(str(ctx.author.id)).get().get('magical_resistance')+1) * dbRef.document(str(ctx.author.id)).get().get('level')}")
							if playerCrited == True:
								newPlayerCard.add_field(name="Dano Causado", value=f"{playerTotalDamage} CRÍTICO!")
							else:
								newPlayerCard.add_field(name="Dano Causado", value=playerTotalDamage)
							newPlayerCard.add_field(name="Dano Recebido", value=0)

							await thisEnemyMsg.edit(embed=newEnemyCard)
							await thisPlayerMsg.edit(embed=newPlayerCard)

							time.sleep(1)

							playerState = "Defendendo"
							enemyState = "Atacando"
					else:
						if thisPlayerHealth <= 0:
							dbRef.document(str(ctx.author.id)).update({
								'gold': dbRef.document(str(ctx.author.id)).get().get('gold') - dbRefCreatures.document(enemyID).get().get('lose_gold')
							})

							await ctx.send(embed=playerLose)
							return
						elif thisEnemyHealth <= 0:
							dbRef.document(str(ctx.author.id)).update({
								'gold': dbRef.document(str(ctx.author.id)).get().get('gold') + dbRefCreatures.document(enemyID).get().get('gold'),
								'xp': dbRef.document(str(ctx.author.id)).get().get('xp') + dbRefCreatures.document(enemyID).get().get('xp')
							})

							if dbRef.document(str(ctx.author.id)).get().get('xp') >= 100 and playerPreviousXP <= 100:
								dbRef.document(str(ctx.author.id)).update({
									'level': 2
								})
								leveledUp = True
							elif dbRef.document(str(ctx.author.id)).get().get('xp') >= 500 and playerPreviousXP <= 500:
								dbRef.document(str(ctx.author.id)).update({
									'level': 3
								})
								leveledUp = True
							elif dbRef.document(str(ctx.author.id)).get().get('xp') >= 1000 and playerPreviousXP <= 1000:
								dbRef.document(str(ctx.author.id)).update({
									'level': 4
								})
								leveledUp = True
							elif dbRef.document(str(ctx.author.id)).get().get('xp') >= 1500 and playerPreviousXP <= 1500:
								dbRef.document(str(ctx.author.id)).update({
									'level': 5
								})
								leveledUp = True
							elif dbRef.document(str(ctx.author.id)).get().get('xp') >= 2500 and playerPreviousXP <= 2500:
								dbRef.document(str(ctx.author.id)).update({
									'level': 6
								})
								leveledUp = True
							elif dbRef.document(str(ctx.author.id)).get().get('xp') >= 3500 and playerPreviousXP <= 3500:
								dbRef.document(str(ctx.author.id)).update({
									'level': 7
								})
								leveledUp = True
							elif dbRef.document(str(ctx.author.id)).get().get('xp') >= 4500 and playerPreviousXP <= 4500:
								dbRef.document(str(ctx.author.id)).update({
									'level': 8
								})
								leveledUp = True
							elif dbRef.document(str(ctx.author.id)).get().get('xp') >= 5500 and playerPreviousXP <= 5500:
								dbRef.document(str(ctx.author.id)).update({
									'level': 9
								})
								leveledUp = True
							elif dbRef.document(str(ctx.author.id)).get().get('xp') >= 6500 and playerPreviousXP <= 6500:
								dbRef.document(str(ctx.author.id)).update({
									'level': 10
								})
								leveledUp = True
							
							if leveledUp == True:
								levelUP = discord.Embed(
									title=":partying_face: Você subiu de nível!",
									description=f"Parabéns! Você avançou para o nível {dbRef.document(str(ctx.author.id)).get().get('level')}"
								)

								await ctx.send(embed=levelUP)

							if dbRefCreatures.document(enemyID).get().get('loot') != None:
								thisItemFormated = dbRefCreatures.document(enemyID).get().get('loot')
								thisItemName = dbRefItems.document(thisItemFormated).get().get('name')
								thisItemDescription = dbRefItems.document(thisItemFormated).get().get('description')
								thisItemType = dbRefItems.document(thisItemFormated).get().get('type')
								

								thisItemEmbed = discord.Embed(
									title=f"Parece que você encontrou um item! => {thisItemName}",
									description=f"{thisItemDescription}"
								)
								if thisItemType == "armorset":
									thisItemEmbed.add_field(name="Armadura :shield:", value=dbRefItems.document(thisItemFormated).get().get('armor'))
									thisItemEmbed.add_field(name="Resistência Mágica :shield", value=dbRefItems.document(thisItemFormated).get().get('magical_resistence'))
								elif thisItemType == "weapon":
									thisItemEmbed.add_field(name="Dano Físico :crossed_swords:", value=dbRefItems.document(thisItemFormated).get().get('physical_damage'))
									thisItemEmbed.add_field(name="Dano Mágico :sparkles:", value=dbRefItems.document(thisItemFormated).get().get('magical_power'))

								thisMsg = await ctx.send(embed=thisItemEmbed)
								await thisMsg.add_reaction('✅')

								i=10
								while True:
									thisItemEmbed.set_footer(text=f"Reaja ao ✅ para receber o item. | {i} segundos restantes")
									await thisMsg.edit(embed=thisItemEmbed)
									if i > 0:
										if verifiers['hasCatchedItem'] == True:
											break
									else:
										await thisMsg.delete()
										return

									time.sleep(1)
									i -= 1

								succesfullyAddedItem = discord.Embed(
									title=":white_check_mark: Item adicionado ao inventário",
									description=f"O item '{thisItemName}' foi adicionado ao seu inventário."
								)

								if thisItemType == "weapon":
									prev = dbRef.document(str(ctx.author.id)).get().get('weapon')

									dbRef.document(str(ctx.author.id)).update({
										'physical_damage': (dbRef.document(str(ctx.author.id)).get().get('physical_damage') - dbRefItems.document(prev).get().get('physical_damage')) + dbRefItems.document(thisItemFormated).get().get('physical_damage'),
										'magical_power': (dbRef.document(str(ctx.author.id)).get().get('magical_power') - dbRefItems.document(prev).get().get('magical_power')) + dbRefItems.document(thisItemFormated).get().get('magical_power'),
										'weapon': dbRefItems.document(thisItemFormated).id
									})
								elif thisItemType == "armorset":
									prev = dbRef.document(str(ctx.author.id)).get().get('armorset')
									
									dbRef.document(str(ctx.author.id)).update({
										'armor': (dbRef.document(str(ctx.author.id)).get().get('armor') - dbRefItems.document(prev).get().get('armor')) + dbRefItems.document(thisItemFormated).get().get('armor'),
										'physical_damage': (dbRef.document(str(ctx.author.id)).get().get('physical_damage') - dbRefItems.document(prev).get().get('physical_damage')) + dbRefItems.document(thisItemFormated).get().get('physical_damage'),
										'armorset': dbRefItems.document(thisItemFormated).id
									})

								await ctx.send(embed=succesfullyAddedItem)

							await ctx.send(embed=playerWon)
							return
						else:
							enemyCrited = False
							if random.randint(0, 100) <= dbRefCreatures.document(enemyID).get().get('crit_chance'):
								enemyTotalDamage += enemyTotalDamage
								enemyCrited = True
							thisPlayerHealth -= enemyTotalDamage

							newEnemyCard = discord.Embed(
								title=f"{dbRefCreatures.document(enemyID).get().get('name')} ({enemyState})",
							)
							newEnemyCard.add_field(name="Pontos de Vida", value=f"{thisEnemyHealth}/{(dbRefCreatures.document(enemyID).get().get('armor')+1)*(dbRefCreatures.document(enemyID).get().get('magical_resistance')+1)*dbRefCreatures.document(enemyID).get().get('difficulty')}")
							if enemyCrited == True:
								newEnemyCard.add_field(name="Dano Causado", value=f"{enemyTotalDamage} CRÍTICO!")
							else:
								newEnemyCard.add_field(name="Dano Causado", value=enemyTotalDamage)
							newEnemyCard.add_field(name="Dano Recebido", value=0)

							newPlayerCard = discord.Embed(
								title=f"{dbRef.document(str(ctx.author.id)).get().get('name')} ({playerState})",
							)
							newPlayerCard.add_field(name="Pontos de Vida", value=f"{thisPlayerHealth}/{(dbRef.document(str(ctx.author.id)).get().get('armor')+1) * (dbRef.document(str(ctx.author.id)).get().get('magical_resistance')+1) * dbRef.document(str(ctx.author.id)).get().get('level')}")
							newPlayerCard.add_field(name="Dano Causado", value=0)
							newPlayerCard.add_field(name="Dano Recebido", value=enemyTotalDamage)

							dbRef.document(str(ctx.author.id)).update({
								'health': dbRef.document(str(ctx.author.id)).get().get('health') - enemyTotalDamage
							})

							await thisEnemyMsg.edit(embed=newEnemyCard)
							await thisPlayerMsg.edit(embed=newPlayerCard)

							time.sleep(1)

							playerState = "Atacando"
							enemyState = "Defendendo"

			await ctx.send(embed=thisEventEmbed)
			return
		
		elif choosedOne == "neutral":
			neutralEvents = db.collection("events").where("type", "==", "neutral")
			thisEvent = random.choice(neutralEvents.get())

			thisEventEmbed = discord.Embed(
				title=f"{thisEvent.get('name')}",
				description=f"{thisEvent.get('description')}"
			)
			thisEventEmbed.set_author(name=ctx.author)
			
			await ctx.send(embed=thisEventEmbed)
			return
		
		elif choosedOne == "good":
			goodEvents = db.collection("events").where("type", "==", "good")
			thisEvent = random.choice(goodEvents.get())

			thisEventEmbed = discord.Embed(
				title=f"{thisEvent.get('name')}",
				description=f"{thisEvent.get('description')}"
			)
			thisEventEmbed.set_author(name=ctx.author)

			if thisEvent.get('item') == None:
				dbRef.document(str(ctx.author.id)).update({
					'gold': dbRef.document(str(ctx.author.id)).get().get('gold') + thisEvent.get('gold'),
					'xp': dbRef.document(str(ctx.author.id)).get().get('xp') + thisEvent.get('xp')
				})
			else:
				thisItemName = dbRefItems.document(thisEvent.get('item')).get().get('name')
				thisItemDescription = dbRefItems.document(thisEvent.get('item')).get().get('description')
				thisItemType = dbRefItems.document(thisEvent.get('item')).get().get('type')
				

				thisItemEmbed = discord.Embed(
					title=f"Parece que você encontrou um item! => {thisItemName}",
					description=f"{thisItemDescription}"
				)
				if thisItemType == "armorset":
					thisItemEmbed.add_field(name="Armadura :shield:", value=dbRefItems.document(thisEvent.get('item')).get().get('armor'))
					thisItemEmbed.add_field(name="Resistência Mágica :shield", value=dbRefItems.document(thisEvent.get('item')).get().get('magical_resistence'))
				elif thisItemType == "weapon":
					thisItemEmbed.add_field(name="Dano Físico :crossed_swords:", value=dbRefItems.document(thisEvent.get('item')).get().get('physical_damage'))
					thisItemEmbed.add_field(name="Dano Mágico :sparkles:", value=dbRefItems.document(thisEvent.get('item')).get().get('magical_power'))

				thisMsg = await ctx.send(embed=thisItemEmbed)
				thisMsg.add_reaction('✅')

				i=10
				while True:
					thisItemEmbed.set_footer(text=f"Reaja ao ✅ para receber o item. | {i} segundos restantes")
					await thisMsg.edit(embed=thisItemEmbed)
					if i > 0:
						if verifiers['hasCatchedItem'] == True:
							break
					else:
						await thisMsg.delete()
						return

					time.sleep(1)
					i -= 1

				succesfullyAddedItem = discord.Embed(
					title=":white_check_mark: Item adicionado ao inventário",
					description=f"O item '{thisItemName}' foi adicionado ao seu inventário."
				)

				if thisItemType == "weapon":
					prev = dbRef.document(str(ctx.author.id)).get().get('weapon')

					dbRef.document(str(ctx.author.id)).update({
						'physical_damage': (dbRef.document(str(ctx.author.id)).get().get('physical_damage') - dbRefItems.document(prev).get().get('physical_damage')) + dbRefItems.document(thisEvent.get('item')).get().get('physical_damage'),
						'magical_power': (dbRef.document(str(ctx.author.id)).get().get('magical_power') - dbRefItems.document(prev).get().get('magical_power')) + dbRefItems.document(thisEvent.get('item')).get().get('magical_power'),
						'weapon': dbRefItems.document(thisEvent.get('item')).id
					})
				elif thisItemType == "armorset":
					prev = dbRef.document(str(ctx.author.id)).get().get('armorset')
					
					dbRef.document(str(ctx.author.id)).update({
						'armor': (dbRef.document(str(ctx.author.id)).get().get('armor') - dbRefItems.document(prev).get().get('armor')) + dbRefItems.document(thisEvent.get('item')).get().get('armor'),
						'physical_damage': (dbRef.document(str(ctx.author.id)).get().get('physical_damage') - dbRefItems.document(prev).get().get('physical_damage')) + dbRefItems.document(thisEvent.get('item')).get().get('physical_damage'),
						'armorset': dbRefItems.document(thisEvent.get('item')).id
					})

				await ctx.send(embed=succesfullyAddedItem)
			
			await ctx.send(embed=thisEventEmbed)
			return

	else:
		await ctx.send(embed=interactionNotFound)

client.run(dataSecrets['token'])
s.close()