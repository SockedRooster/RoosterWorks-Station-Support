"""Limit only this worker process; never change the user's interactive Blender."""
import os

def limit_worker(cores=2):
    for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
        os.environ[key]=str(cores)
    if os.name=='nt':
        import ctypes
        from ctypes import wintypes
        k=ctypes.WinDLL('kernel32',use_last_error=True)
        k.GetCurrentProcess.restype=wintypes.HANDLE
        handle=k.GetCurrentProcess()
        k.SetPriorityClass.argtypes=[wintypes.HANDLE,wintypes.DWORD]
        if not k.SetPriorityClass(handle,0x40):raise ctypes.WinError(ctypes.get_last_error())
        process=ctypes.c_size_t();system=ctypes.c_size_t()
        k.GetProcessAffinityMask.argtypes=[wintypes.HANDLE,ctypes.POINTER(ctypes.c_size_t),ctypes.POINTER(ctypes.c_size_t)]
        k.SetProcessAffinityMask.argtypes=[wintypes.HANDLE,ctypes.c_size_t]
        if not k.GetProcessAffinityMask(handle,ctypes.byref(process),ctypes.byref(system)):raise ctypes.WinError(ctypes.get_last_error())
        allowed=[1<<i for i in range(ctypes.sizeof(process)*8) if process.value&(1<<i)]
        if not k.SetProcessAffinityMask(handle,sum(allowed[:cores])):raise ctypes.WinError(ctypes.get_last_error())
