#include "inject.h"

// Shared variables to be manipulated externally
#pragma data_seg("SHARED")
DWORD tickCount = 0;
#pragma data_seg()


// Functions to inject
DWORD GetTickCount() {
    return tickCount;
}


// Externally exposed functions
extern "C" __declspec(dllexport)
void setTickCount(unsigned long newTickCount) {
    tickCount = newTickCount;
}

#pragma comment(linker, "/section:SHARED,RWS")