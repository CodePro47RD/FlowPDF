"""
ReportForge v2.0 Python Native In-Process Binding (ctypes).
Directly executes the compiled Rust engine in-process with zero network overhead.
"""

import ctypes
import os
import sys
from typing import Optional, Union
import json


class _ReportForgeResult(ctypes.Structure):
    _fields_ = [
        ("data", ctypes.POINTER(ctypes.c_uint8)),
        ("length", ctypes.c_size_t),
        ("success", ctypes.c_bool),
        ("error_message", ctypes.c_char_p),
    ]


class ReportForgeEngine:
    _lib = None

    @classmethod
    def _get_lib(cls):
        if cls._lib is not None:
            return cls._lib

        # Localizar el archivo binario (.dll, .so, .dylib)
        candidates = [
            "reportforge.dll",
            "libreportforge.so",
            "libreportforge.dylib",
            os.path.join(os.path.dirname(__file__), "..", "..", "engine-rust", "target", "release", "reportforge.dll"),
            os.path.join(os.path.dirname(__file__), "..", "..", "engine-rust", "target", "release", "libreportforge.so"),
        ]

        lib_path = None
        for candidate in candidates:
            if os.path.exists(candidate):
                lib_path = os.path.abspath(candidate)
                break

        if not lib_path:
            lib_path = "reportforge"  # Dejar que el sistema operativo lo resuelva en PATH/LD_LIBRARY_PATH

        cls._lib = ctypes.CDLL(lib_path)

        cls._lib.reportforge_render_pdf.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        cls._lib.reportforge_render_pdf.restype = _ReportForgeResult

        cls._lib.reportforge_free_result.argtypes = [_ReportForgeResult]
        cls._lib.reportforge_free_result.restype = None

        cls._lib.reportforge_version.argtypes = []
        cls._lib.reportforge_version.restype = ctypes.c_char_p

        return cls._lib

    @classmethod
    def version(cls) -> str:
        lib = cls._get_lib()
        return lib.reportforge_version().decode("utf-8")

    @classmethod
    def render_pdf(cls, document: Union[dict, str], data: Optional[Union[dict, str]] = None) -> bytes:
        lib = cls._get_lib()

        doc_json = json.dumps(document) if isinstance(document, dict) else document
        doc_cstr = doc_json.encode("utf-8")

        data_cstr = None
        if data is not None:
            data_json = json.dumps(data) if isinstance(data, dict) else data
            data_cstr = data_json.encode("utf-8")

        result = lib.reportforge_render_pdf(doc_cstr, data_cstr)

        try:
            if not result.success:
                err_msg = result.error_message.decode("utf-8") if result.error_message else "Unknown native error"
                raise RuntimeError(f"ReportForge Native Error: {err_msg}")

            if result.length == 0 or not result.data:
                return b""

            # Copiar bytes de memoria nativa a bytes de Python
            buffer_type = ctypes.c_uint8 * result.length
            buffer = buffer_type.from_address(ctypes.addressof(result.data.contents))
            return bytes(buffer)
        finally:
            lib.reportforge_free_result(result)
