# Write-Up CVE4Free

Ce challenge utilise cve-rs pour implementer un buffer-overflow dans rust.

Il suffit de trouver le username et ensuite de mettre assez de data dans le buffer pour que is_admin ne soit plus egal a 0.

Cette payload fonctionne:
```
adminthelionkingadminthelionkingadminthelionking
```
