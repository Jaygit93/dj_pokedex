from django.db import models

class Ability(models.Model):
    abil_name = models.CharField(max_length=79)

    objects = models.Manager()

    class Meta:
        db_table = 'abilities'


class Type(models.Model):
    type_name = models.CharField(max_length=50, unique=True)
    colors = models.CharField(max_length=7)
    
    objects = models.Manager()

    class Meta:
        db_table = 'types'


class Pokemon(models.Model):
    pok_name = models.CharField(max_length=79)
    pok_height = models.IntegerField(null=True, blank=True)
    pok_weight = models.IntegerField(null=True, blank=True)
    pok_base_experience = models.IntegerField(null=True, blank=True)
    pok_cries = models.CharField(max_length=255, null=True, blank=True)
    pok_sprites = models.CharField(max_length=255, null=True, blank=True)

    objects = models.Manager()

    class Meta:
        db_table = 'pokemon'



class PokemonAbility(models.Model):
    pok_id = models.ForeignKey(Pokemon, on_delete=models.CASCADE, db_column="pok_id")
    abil_id = models.ForeignKey(Ability, on_delete=models.CASCADE, db_column="abil_id")
    is_hidden = models.BooleanField(default=False)
    slot = models.IntegerField()

    objects = models.Manager()

    class Meta:
        unique_together = ('pok_id', 'abil_id', 'slot')
        db_table = 'pokemon_abilities'


class BaseStats(models.Model):
    pok_id = models.OneToOneField(Pokemon, on_delete=models.CASCADE, primary_key=True, db_column="pok_id")
    b_hp = models.IntegerField(null=True, blank=True)
    b_atk = models.IntegerField(null=True, blank=True)
    b_def = models.IntegerField(null=True, blank=True)
    b_sp_atk = models.IntegerField(null=True, blank=True)
    b_sp_def = models.IntegerField(null=True, blank=True)
    b_speed = models.IntegerField(null=True, blank=True)
    
    objects = models.Manager()

    class Meta:
        db_table = 'base_stats'


class PokemonType(models.Model):
    pok_id = models.ForeignKey(Pokemon, on_delete=models.CASCADE, db_column="pok_id")
    type_id = models.ForeignKey(Type, on_delete=models.CASCADE, db_column="type_id")
    slot = models.IntegerField()

    objects = models.Manager()

    class Meta:
        unique_together = ('pok_id', 'type_id', 'slot')  # Contrainte d'unicité
        db_table = 'pokemon_types'
        
        
class PokemonDescription(models.Model):
    pok_id = models.ForeignKey('Pokemon', on_delete=models.CASCADE, db_column="pok_id")
    flavor_text = models.TextField()  # Utilisation de TextField pour stocker des descriptions longues
    nickname = models.CharField(max_length=255, null=True, blank=True)
    
    objects = models.Manager()
    
    class Meta:
        db_table = 'pokemon_description'
        # Indexation sur 'pok_id' pour améliorer la recherche basée sur la clé étrangère
        indexes = [
            models.Index(fields=['pok_id']),
        ]
        
        
        

class TypeEfficacy(models.Model):
    # Clé primaire composée : type de l'attaque et type de la cible
    damage_type = models.ForeignKey('Type', on_delete=models.CASCADE, related_name='attacking_type', db_column='damage_type_id')
    target_type = models.ForeignKey('Type', on_delete=models.CASCADE, related_name='defending_type', db_column='target_type_id')
    # Facteur de dégâts (ex : 200 = x2, 50 = x0.5, 0 = inefficace)
    damage_factor = models.IntegerField()
    
    objects = models.Manager()

    class Meta:
        db_table = 'type_efficacy'
        unique_together = ('damage_type', 'target_type')  # Contrainte d'unicité
        indexes = [
            models.Index(fields=['damage_type']),
            models.Index(fields=['target_type']),
        ]
        