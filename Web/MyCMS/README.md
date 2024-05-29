**Titre**: MyCMS <br>
**Difficulté**: Very Hard <br>
**Auteur**: Worty <br>

**Dist**: MyCMS.zip 

Pour les testeurs, il vous faut la commande `composer` et il faut exécuter dans `src/` la commande: `composer install`.

```bash
cd MyCMS/src/src
docker run --rm --interactive --tty --volume $PWD:/app composer install --ignore-platform-req=ext-gd
```
