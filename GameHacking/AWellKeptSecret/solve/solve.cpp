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
