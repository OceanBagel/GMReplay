#include <windows.h>

DWORD GetTickCount(void);

extern "C" __declspec(dllexport) void setTickCount(unsigned long newTickCount);