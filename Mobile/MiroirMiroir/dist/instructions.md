Développez une application capable de déverouiller l'écran d'un appareil Android, sans aucune permission, ni connaissance du code PIN/mot de passe/schéma.  

La `system-image` Android est fournie en pièce jointe, mais vous pouvez utiliser les versions disponibles dans le SDK manager, respectant les conditions suivantes : 

- `Android 14`
- `ro.build.version.security_patch` < 2023-12-01 / 01 décembre 2023 (`adb shell getprop ro.build.version.security_patch`)

Exemple conseillé : `system-images;android-34;google_apis;x86_64`. Vérifiez tout de même si les conditions précédentes sont respectées.

Une fois votre exploit validé en local, vous pourrez le soumettre à un émulateur distant, disponible via une interface graphique Web.

L'émulateur réalisera les actions suivantes : 

- Démarrage de l'émulateur
- Verrouillage de l'écran
- Première capture d'écran
- Exécution de votre APK, via `adb`, qui sera laissé en tâche de fond
- Exécution de l'application de flag, et passage de cette application au premier plan.
- Deuxième capture d'écran

Plusieurs secondes peuvent s'écouler entre chaque étape, afin de s'assurer de leur prise en compte. Si votre APK a déverrouillé l'écran, le flag sera affiché dans la deuxième capture d'écran.
