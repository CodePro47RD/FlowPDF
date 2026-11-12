"""
Native C-ABI bindings for ReportForge v2.0 (Rust Core).
Provides ultra-high performance in-process PDF rendering with zero network latency.
"""

from __future__ import annotations
import ctypes
from ctypes import c_char_p, c_size_t, c_bool, c_void_p, POINTER, Structure
import json
import os
import platform
import sys
from typing import Any, Dict, Optional, Union


class ReportForgeResult(Structure):
    _fields_ = [
        ("data", POINTER(ctypes.c_ubyte)),
        ("length", c_size_t),
        ("success", c_bool),
        ("error_message", c_char_p),
    ]


class ReportForgeEngine:
    """
    In-process Rust Core v2.0 rendering engine.
    Renders ReportForge documents into PDF bytes in ~15ms - 45ms.
    """
    _lib = None

    @classmethod
    def _find_library(cls) -> str:
        system = platform.system()
        if system == "Windows":
            rid = "win-x64"
            filename = "reportforge_native.dll"
        elif system == "Darwin":
            rid = "osx-x64"
            filename = "libreportforge_native.dylib"
        else:
            rid = "linux-x64"
            filename = "libreportforge_native.so"

        base_dir = os.path.dirname(os.path.abspath(__file__))

        candidates = [
            os.path.join(base_dir, "runtimes", rid, "native", filename),
            os.path.join(base_dir, "runtimes", rid, filename),
            os.path.join(base_dir, filename),
            os.path.join(os.getcwd(), "runtimes", rid, "native", filename),
            os.path.join(base_dir, "..", "..", "..", "engine-rust", "target", "x86_64-pc-windows-gnu", "release", "reportforge.dll"),
            os.path.join(base_dir, "..", "..", "..", "engine-rust", "target", "release", "libreportforge.so"),
            filename,
        ]

        for cand in candidates:
            if os.path.isfile(cand):
                return os.path.abspath(cand)

        return filename

    @classmethod
    def _get_lib(cls):
        if cls._lib is None:
            lib_path = cls._find_library()
            try:
                cls._lib = ctypes.CDLL(lib_path)
            except Exception as e:
                raise RuntimeError(
                    f"ReportForge Native Error: Could not load native library from '{lib_path}'. "
                    f"Ensure embedded runtimes are present or on system PATH. Error: {e}"
                )

            cls._lib.reportforge_render_pdf.argtypes = [c_char_p, c_char_p]
            cls._lib.reportforge_render_pdf.restype = ReportForgeResult

            cls._lib.reportforge_free_result.argtypes = [ReportForgeResult]
            cls._lib.reportforge_free_result.restype = None

            cls._lib.reportforge_version.argtypes = []
            cls._lib.reportforge_version.restype = c_char_p

        return cls._lib

    @classmethod
    def get_version(cls) -> str:
        """Returns the version banner of the loaded native Rust Core."""
        lib = cls._get_lib()
        raw = lib.reportforge_version()
        return raw.decode("utf-8") if raw else "ReportForge Rust Core v2.0"

    @classmethod
    def render_pdf(
        cls,
        document: Union[Dict[str, Any], str, Any],
        data: Optional[Union[Dict[str, Any], str, list]] = None,
    ) -> bytes:
        """
        Renders a document definition AST directly to PDF bytes in-process using Rust Core v2.0.
        Execution speed is typically 15ms - 50ms with zero network overhead.
        """
        if hasattr(document, "build") and callable(document.build):
            document = document.build()

        doc_json = json.dumps(document, ensure_ascii=False) if isinstance(document, dict) else str(document)
        data_json = (
            json.dumps(data, ensure_ascii=False)
            if isinstance(data, (dict, list))
            else (str(data) if data is not None else None)
        )

        doc_bytes = doc_json.encode("utf-8")
        data_bytes = data_json.encode("utf-8") if data_json is not None else None

        lib = cls._get_lib()
        result = lib.reportforge_render_pdf(doc_bytes, data_bytes)

        try:
            if not result.success:
                err_msg = (
                    result.error_message.decode("utf-8")
                    if result.error_message
                    else "Unknown native error"
                )
                raise RuntimeError(f"ReportForge Native Error: {err_msg}")

            if result.length > 0 and result.data:
                # Copy from C pointer to Python bytes
                pdf_bytes = bytes(result.data[: result.length])
                return pdf_bytes
            return b""
        finally:
            lib.reportforge_free_result(result)
