import requests
from django.shortcuts import render, get_object_or_404
from .models import Pokemon, PokemonType, BaseStats, PokemonDescription, PokemonAbility, Ability, TypeEfficacy, Type

def pokemon_list(request):
    """Affiche tous les Pokémon avec filtres par nom, type, et numéros"""

    # Définition manuelle des types
    all_types = [
        "Normal", "Fire", "Water", "Electric", "Grass", "Ice", "Fighting", "Poison",
        "Ground", "Flying", "Psychic", "Bug", "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy"
    ]

    # Filtrage par type, ability, nom, et intervalle
    type_filter = request.GET.get('type', '')
    second_type_filter = request.GET.get('second_type', '')
    name_filter = request.GET.get('name', '')
    number_min = request.GET.get('number_min', '')
    number_max = request.GET.get('number_max', '')

    # Vérification des bornes min/max
    try:
        number_min = max(1, int(number_min)) if number_min.isdigit() else 1
        number_max = min(721, int(number_max)) if number_max.isdigit() else 721
    except ValueError:
        number_min, number_max = 1, 721

    pokemons = Pokemon.objects.all()

    if name_filter:
        pokemons = pokemons.filter(pok_name__icontains=name_filter)

    if type_filter:
        pokemons = pokemons.filter(pokemontype__type_id__type_name=type_filter).distinct()

    if second_type_filter:
        pokemons = pokemons.filter(pokemontype__type_id__type_name=second_type_filter).distinct()

    pokemons = pokemons.filter(id__gte=number_min, id__lte=number_max)

    # Récupération des types associés à chaque Pokémon
    pokemon_data = []
    for pokemon in pokemons:
        types = list(PokemonType.objects.filter(pok_id=pokemon).select_related('type_id'))
        type_names = [t.type_id.type_name for t in types]

        # Attribution des couleurs des types
        type_colors = {
            "Fire": "#F08030", "Water": "#6890F0", "Grass": "#78C850", "Electric": "#F8D030",
            "Ice": "#98D8D8", "Fighting": "#C03028", "Poison": "#A040A0", "Ground": "#E0C068",
            "Flying": "#A890F0", "Psychic": "#F85888", "Bug": "#A8B820", "Rock": "#B8A038",
            "Ghost": "#705898", "Dragon": "#7038F8", "Dark": "#705848", "Steel": "#B8B8D0",
            "Fairy": "#EE99AC", "Normal": "#A8A878"
        }
        background_color = type_colors.get(type_names[0], "#A8A878")  # Par défaut, couleur "Normal"

        # Si double type, mélange des couleurs (dégradé)
        if len(type_names) > 1:
            bg_color_1 = type_colors.get(type_names[0], "#A8A878")
            bg_color_2 = type_colors.get(type_names[1], "#A8A878")
            background_color = f"linear-gradient(to right, {bg_color_1}, {bg_color_2})"

        pokemon_data.append({
            "id": pokemon.id,
            "name": pokemon.pok_name,
            "types": type_names,
            "sprite": f"/static/sprites/{pokemon.id}.png",
            "cry": f"/static/cries/{pokemon.id}.ogg",
            "background": background_color
        })

    return render(request, "pokemon_list.html", {
        "pokemon_data": pokemon_data,
        "all_types": all_types,
        "number_min": number_min,
        "number_max": number_max
    })



def calculate_effectiveness(pokemon):
    """Calcule les résistances et faiblesses du Pokémon avec gestion des immunités"""
    types = PokemonType.objects.filter(pok_id=pokemon).select_related('type_id')
    type_names = [t.type_id for t in types]

    effectiveness = {
        "weaknesses": set(),
        "resistances": set(),
        "double_weaknesses": set(),
        "double_resistances": set(),
        "immunities": set()
    }

    # Parcours des types du Pokémon
    for target_type in type_names:
        # Récupération de l'efficacité de chaque type
        type_eff = TypeEfficacy.objects.filter(target_type=target_type)

        for eff in type_eff:
            factor = eff.damage_factor / 100

            # Cas d'immunité (facteur 0)
            if factor == 0:
                effectiveness["immunities"].add(eff.damage_type.type_name)
            
            # Cas de résistance (facteur 0.5 ou 0.25)
            elif factor == 0.5:
                effectiveness["resistances"].add(eff.damage_type.type_name)
            elif factor == 0.25:
                effectiveness["double_resistances"].add(f"{eff.damage_type.type_name} /4")
            
            # Cas de faiblesse (facteur 2 ou 4)
            elif factor == 2:
                effectiveness["weaknesses"].add(eff.damage_type.type_name)
            elif factor == 4:
                effectiveness["double_weaknesses"].add(f"{eff.damage_type.type_name} x4")

    # Maintenant, on gère les interactions entre les deux types
    neutralized_weaknesses = set()
    neutralized_resistances = set()

    for type_name in type_names:
        # On vérifie si l'un des types neutralise les faiblesses ou résistances de l'autre
        for eff in TypeEfficacy.objects.filter(target_type=type_name):
            factor = eff.damage_factor / 100

            if factor == 0.5 and eff.damage_type.type_name in effectiveness["weaknesses"]:
                neutralized_weaknesses.add(eff.damage_type.type_name)
            if factor == 2 and eff.damage_type.type_name in effectiveness["resistances"]:
                neutralized_resistances.add(eff.damage_type.type_name)

    # On retire les faiblesses et résistances neutralisées
    effectiveness["weaknesses"] -= neutralized_weaknesses
    effectiveness["resistances"] -= neutralized_resistances

    # On retire les immunités des faiblesses et résistances
    effectiveness["weaknesses"] -= effectiveness["immunities"]
    effectiveness["resistances"] -= effectiveness["immunities"]

    # Conversion des sets en listes pour l'affichage
    effectiveness["weaknesses"] = list(effectiveness["weaknesses"])
    effectiveness["resistances"] = list(effectiveness["resistances"])
    effectiveness["double_weaknesses"] = list(effectiveness["double_weaknesses"])
    effectiveness["double_resistances"] = list(effectiveness["double_resistances"])
    effectiveness["immunities"] = list(effectiveness["immunities"])

    return effectiveness



def get_stat_color(value):
    if value >= 150:
        return "#1982c4"
    elif value >= 120:
        return "#8ac926"
    elif value >= 90:
        return "#ffca3a"
    elif value >= 60:
        return "#ff924c"
    elif value >= 30:
        return "#f00007"
    else:
        return "#6a4c93"
    
    
    
def get_evolution_chain(evolution_chain_url):
    """ Récupère toute la chaîne d'évolution depuis PokéAPI, en prenant en compte les évolutions alternatives. """
    response = requests.get(evolution_chain_url)
    if response.status_code != 200:
        return []

    data = response.json()
    chain = data['chain']
    
    evolution_paths = []  # Liste pour stocker toutes les évolutions possibles

    def parse_evolution(chain, path=[]):
        """Parcourt récursivement la chaîne d'évolution pour inclure toutes les évolutions alternatives."""
        species_name = chain['species']['name'].capitalize()
        new_path = path + [species_name]  # Ajoute l'évolution actuelle au chemin
        
        if not chain['evolves_to']:  # Si pas d'évolution supplémentaire
            evolution_paths.append(" > ".join(new_path))  # Ajoute le chemin final
        else:
            for evolution in chain['evolves_to']:
                parse_evolution(evolution, new_path)  # Récursion pour chaque évolution alternative

    parse_evolution(chain)
    
    return evolution_paths


def pokemon_detail(request, pok_id):
    """Affiche les détails d'un Pokémon"""
    pokemon = get_object_or_404(Pokemon, id=pok_id)
    stats = BaseStats.objects.filter(pok_id=pokemon).first()
    abilities = PokemonAbility.objects.filter(pok_id=pokemon).select_related('abil_id')
    types = PokemonType.objects.filter(pok_id=pokemon).select_related('type_id')
    description = PokemonDescription.objects.filter(pok_id=pokemon).first()
    effectiveness = calculate_effectiveness(pokemon)

    nickname = description.nickname if description else None
    
    # Attribution des couleurs des types
    type_names = [t.type_id.type_name for t in types]
    type_colors = {
        "Fire": "#F08030", "Water": "#6890F0", "Grass": "#78C850", "Electric": "#F8D030",
        "Ice": "#98D8D8", "Fighting": "#C03028", "Poison": "#A040A0", "Ground": "#E0C068",
        "Flying": "#A890F0", "Psychic": "#F85888", "Bug": "#A8B820", "Rock": "#B8A038",
        "Ghost": "#705898", "Dragon": "#7038F8", "Dark": "#705848", "Steel": "#B8B8D0",
        "Fairy": "#EE99AC", "Normal": "#A8A878"
    }
    background_color = type_colors.get(type_names[0], "#A8A878")  # Par défaut, couleur "Normal"

    # Si double type, mélange des couleurs (dégradé)
    if len(type_names) > 1:
        bg_color_1 = type_colors.get(type_names[0], "#A8A878")
        bg_color_2 = type_colors.get(type_names[1], "#A8A878")
        background_color = f"linear-gradient(to right, {bg_color_1}, {bg_color_2})"

    # Récupérer l'URL de la chaîne d'évolution depuis PokéAPI
    species_url = f"https://pokeapi.co/api/v2/pokemon-species/{pok_id}/"
    species_data = requests.get(species_url).json()
    evolution_chain_url = species_data['evolution_chain']['url']

    # Récupérer la famille d'évolution complète (liste de chaînes)
    evolution_family_paths = get_evolution_chain(evolution_chain_url)

    # Pour chaque chaîne d'évolution, transformer chaque nom en dictionnaire (id, nom, sprite)
    evolution_data = []
    for path in evolution_family_paths:
        names = path.split(" > ")
        chain = []
        for name in names:
            try:
                # Recherche insensible à la casse pour être sûr de récupérer le bon Pokémon
                pok = Pokemon.objects.get(pok_name__iexact=name)
                chain.append({
                    "id": pok.id,
                    "name": pok.pok_name,
                    "sprite": f"/static/sprites/{pok.id}.png"
                })
            except Pokemon.DoesNotExist:
                # Si le Pokémon n'est pas trouvé dans la BDD, on peut l'ignorer
                pass
        evolution_data.append(chain)
    
    # Organisation des stats sous forme de dictionnaire
    stats = {
        "HP": stats.b_hp,
        "Attaque": stats.b_atk,
        "Défense": stats.b_def,
        "Attaque Spé.": stats.b_sp_atk,
        "Défense Spé.": stats.b_sp_def,
        "Vitesse": stats.b_speed,
    }

    # Normalisation des statistiques sur 200 et ajout des couleurs
    stats_info = {
        stat: {
            "value": value,
            "percentage": (value / 200) * 100,
            "color": get_stat_color(value),
        }
        for stat, value in stats.items()
    }
    
    # Trouver l'ID du Pokémon précédent et suivant
    previous_pokemon = Pokemon.objects.filter(id__lt=pok_id).order_by('-id').first()
    next_pokemon = Pokemon.objects.filter(id__gt=pok_id).order_by('id').first()

    context = {
        "pokemon": pokemon,
        "stats_info": stats_info,
        "abilities": [a.abil_id.abil_name for a in abilities],
        "types": [t.type_id.type_name for t in types],
        "description": description,
        "effectiveness": effectiveness,
        "evolution_data": evolution_data,
        "sprite": f"/static/sprites/{pokemon.id}.png",
        "cry": f"/static/cries/{pokemon.id}.ogg",
        "background_color": background_color, 
        "nickname": nickname,
        'previous_pokemon_id': previous_pokemon.id if previous_pokemon else pok_id,
        'next_pokemon_id': next_pokemon.id if next_pokemon else pok_id,
    }

    return render(request, "pokemon_detail.html", context)
