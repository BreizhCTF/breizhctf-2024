
_Vous voici arrivé à l'ultime tâche que doit réaliser Galahad, et pas des moindres : retrouver la puissante Excalibur, l'épée du Roi Arthur. Ce dernier l'a perdue quelque part sur la carte, et loin de son maître, l'arme est devenue invisible. Il vous faut donc rentrer en contact avec un objet invisible perdu à un endroit quelconque..._

# Introduction

Il est important de préciser que la solution ici présentée n'est pas la seule susceptible de fonctionner.

# I - Analyse de l'objectif

Pour cette tâche, vous pourrez tourner aussi longtemps que vous le voulez sur la carte, vous ne tomberez pas sur Excalibur par magie. Il vous faut trouver un moyen (en fouillant dans la mémoire) de retrouver les coordonnées de l'épée et de la percuter pour la faire apparaître (et le flag par la même occasion).

# II - Scanning mémoire

La première étape est de retrouver vos coordonnées en mémoire. Si vous avez déjà effectué `Only Up!`, vous savez comment trouver votre coordonnée `Y` (hauteur) sinon je vous invite à lire le write-up concernant ce challenge. Bon nous avons `Y` comment trouvons-nous `X` et `Z`. Bien qu'il serait possible d'effectuer des scans en supposant que ces valeurs évoluent dans tel ou tel sens en prenant des axes invisibles, les triplets de coordonnées sont bien souvent rassemblés dans la mémoire car ces variables sont déclarées les unes à côté des autres par les développeurs. Faites un clic droit sur votre variable `Y` puis sélectionnez `Browse this memory region`.

![](wu_images/Screenshot%202024-05-12%20002905.png)

Une vue s'ouvre alors et en-dessous du désassembleur vous constaterez un éditeur hexadécimal à l'adresse de votre variable `Y`. Faites un clic droit dans cette vue puis `Display Type > Float` pour que l'éditeur hexadécimal regroupe ses valeurs en 4 octets sour forme de nombre flottants.

![](wu_images/Screenshot%202024-05-12%20003002.png)

On constate alors que la valeur avant `Y` a bien une allure de `float`, tout comme la valeur après `Y`. On a sans doute trouvé `X` et `Z`.

![](wu_images/Screenshot%202024-05-12%20003030.png)

Ajoutez ces variables à votre liste puis amusez-vous à les cocher pour voir si votre personnage reste bloqué sur un axe.

![](wu_images/Screenshot%202024-05-12%20003121.png)

Si cela semble fonctionner, vous remarquerez peut-être des sortes de sauts semblant vous forcer à revenir à votre position normale. Pour empêcher cela, observez les instructions assembleurs qui éditent vos différentes variables de position.

![](wu_images/Screenshot%202024-05-12%20003215.png)

Sans marcher, une instruction passe son temps à éditer notre variable, vous ne souhaitez pas la patcher car elle est en fait liée au déplacement de votre caméra et modifier cette instruction reviendrait à décrocher la caméra du joueur.  
En revanche, lorsque vous marchez, une autre instruction édite notre variable.

![](wu_images/Screenshot%202024-05-12%20003259.png)

Cliquez sur `Show disassembler` après avoir sélectionné cette variable. Dans la vue désassembleur, sélectionnez l'instruction puis `Clic droit > Replace with code that does nothing` pour la remplacer par des `NOP`.

![](wu_images/Screenshot%202024-05-12%20003335.png)

Vous devriez avoir davantage de maîtrise sur le déplacement de votre personnage. Et c'est capital vous allez comprendre pourquoi.  
Toujours dans la vue désassembleur, sous `View` choisissez `Memory Regions` pour afficher l'ensemble des zones mémoires de votre programme.

![](wu_images/Screenshot%202024-05-12%20004041.png)

Rendez-vous alors à la zone mémoire qui contient les adresses de vos coordonnées et notez bien son adresse de début et de fin. En effet, dans cette partie du tas se trouvent les différents objets du moteur Unity. Dont notre objet invisible.

# III - Scripting WinAPI

L'idée est simple, lire l'ensemble de cette région mémoire à la recherche de triplets de coordonnées. Chaque fois que nous en trouvons un, nous téléportons le joueur sur la position du triplet pendant une seconde. Il est important de continuer à marcher durant les téléportations car il faut être sûr de bien déclencher une collision. Toute la technique réside dans le fait de trier des triplets logiques, à savoir pas situés à 10 millions de mètres du spawn, non-égaux à 0,0,0...  
Je vous propose le script suivant, qu'il faut légèrement éditer pour changer les adresses mémoire de la région scannée et des coordonnées du joueur.

```c
#include <Windows.h>
#include <tlhelp32.h>
#include <stdio.h>
#include <psapi.h>
#include <math.h>

using namespace std;

HANDLE FindProc(const wchar_t* proc_name) {
    PROCESSENTRY32 entry;
    entry.dwSize = sizeof(PROCESSENTRY32);
    HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (Process32First(snapshot, &entry) == TRUE)
    {
        while (Process32Next(snapshot, &entry) == TRUE)
        {
            if (!_wcsicmp(entry.szExeFile, proc_name))
            {
                HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, entry.th32ProcessID);
                return hProcess;
            }
        }
    }
    CloseHandle(snapshot);
    return 0;
}

HMODULE GetModule(HANDLE pHandle, const wchar_t* proc_name)
{
    HMODULE hMods[1024];
    DWORD cbNeeded;
    unsigned int i;

    if (EnumProcessModules(pHandle, hMods, sizeof(hMods), &cbNeeded))
    {
        for (i = 0; i < (cbNeeded / sizeof(HMODULE)); i++)
        {
            TCHAR szModName[MAX_PATH];
            if (GetModuleFileNameEx(pHandle, hMods[i], szModName, sizeof(szModName) / sizeof(TCHAR)))
            {
                if (wcsstr(szModName, proc_name))
                {
                    return hMods[i];
                }
            }
        }
    }
    return NULL;
}

int main() {
    HANDLE proc = FindProc(L"Galahad Quest.exe");
    HMODULE baseMod = GetModule(proc, L"Galahad Quest.exe");
    UINT64 heap_start = 0x14200000000;
    UINT64 heap_end = 0x142000FFFFF;
    FLOAT* buff = (FLOAT*) malloc(1024);
    UINT64 off = heap_start;
    FLOAT f1, f2 = 100000, f3 = 100000;
    while (off < heap_end) {
        ReadProcessMemory(proc, (LPCVOID)off, buff, 1024, NULL);
        off += 1024;
        for (UINT64 i = 0; i < 1024 / sizeof(FLOAT); i++) {
            f1 = buff[i];
            if (f1 >= -10000.0 && f1 <= 10000.0 && f2 >= -10000.0 && f2 <= 10000.0 && f3 >= -10000.0 && f3 <= 10000.0 && (f1 >= 0.1 || f1 <= -0.1) && (f2 >= 0.1 || f2 <= -0.1) && (f3 >= 0.1 || f3 <= -0.1) && (pow(f1-f2, 2) >= 0.1 || pow(f1 - f3, 2) >= 0.1)) {
                printf("%6.3f %6.3f %6.3f\n", f3, f2, f1);
                WriteProcessMemory(proc, (LPVOID)0x142000DBA50, &f3, sizeof(f3), 0);
                WriteProcessMemory(proc, (LPVOID)0x142000DBA54, &f2, sizeof(f2), 0);
                WriteProcessMemory(proc, (LPVOID)0x142000DBA58, &f1, sizeof(f1), 0);
                Sleep(1000);
            }
            f3 = f2;
            f2 = f1;
        }
    }
}
```

# Résolution

En lançant le script, vous finirez pas tomber sur le triplet (06,02,1934) là où se situe Excalibur. Lors de votre téléportation, si vous marchez légèrement elle apparaîtra ainsi que le flag.

![](wu_images/Screenshot%202024-05-12%20004850.png)

Voici donc le flag `BZHCTF{take_it_back_to_king_arthur}`

# Conclusion

Ce challenge avait pour but de laisser le joueur en autonomie sur la conception d'une méthode pour localiser un objet sans apparence dans un jeu Unity. Il me paraît difficile de le résoudre sans scripter et je pense donc que c'est une bonne introduction pour s'essayer à la WinAPI.
