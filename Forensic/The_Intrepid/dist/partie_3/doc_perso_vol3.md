Au taff, un gars m'avait parlé d'un outil intégré à Volatility avec lequel on pouvait faire de l'analyse mémoire manuelle. 

TODO: Lui re-demander le nom exact.

J'ai quand même retrouvé un bout de sa doc : 

```python
# Tips : pense bien à lancer ce tool avec l'option `-l` pour un dump Linux 

"""Une fois que tu es dedans, t'auras accès à une console interactive.
Je te montre comment créer un objet en mémoire :"""

# Déclarer l'objet kernel
kernel = self.context.modules[self.config["kernel"]]

# Construire un objet du kernel, en se basant sur son type et son adresse en mémoire 
objet = kernel.object(*type_objet*, *adresse_objet*, absolute=True) 

# Le type de l'objet, tu le passes sous forme de string (ex: "task" ou "proc"). Ensuite, tu pourras inspecter ton objet, avec les fonctions dispo dans l'aide.
help()
```
