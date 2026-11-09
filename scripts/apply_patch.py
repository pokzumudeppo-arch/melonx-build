"""Clamp the GPU texture cache on iOS (see README). Fails loudly if the code changed."""
import re, sys, pathlib

p = pathlib.Path(sys.argv[1]) / "src/Ryujinx.Graphics.Gpu/Image/AutoDeleteCache.cs"
s = p.read_text()

if "IosTextureSizeCapacity" in s:
    print("Patch already present"); sys.exit(0)

const_anchor = "private const ulong DefaultTextureSizeCapacity"
if const_anchor not in s or "MaximumGpuMemory * MemoryScaleFactor" not in s:
    print("::error::AutoDeleteCache.cs no longer matches the expected code; patch not applied")
    sys.exit(1)

s = re.sub(r"(\n(\s*)private const ulong DefaultTextureSizeCapacity[^\n]*\n)",
           r"\1\2private const ulong IosTextureSizeCapacity = 1UL * 1024 * 1024 * 1024;\n", s, count=1)

m = re.search(r"public void Initialize\(GpuContext context\)\s*\{", s)
depth, i = 1, m.end()
while depth:
    depth += {"{": 1, "}": -1}.get(s[i], 0); i += 1
close = i - 1
indent = "            "
clamp = (f"\n{indent}// iOS: MoltenVK reports nearly all unified RAM as device-local GPU memory,\n"
         f"{indent}// so the 50% rule gives a ~3.75 GiB cache on an 8 GB iPhone, above what the\n"
         f"{indent}// ~6 GiB per-app limit leaves after guest DRAM. Jetsam kills the app first.\n"
         f"{indent}if (OperatingSystem.IsIOS())\n{indent}{{\n"
         f"{indent}    _maxCacheMemoryUsage = Math.Min(_maxCacheMemoryUsage, IosTextureSizeCapacity);\n"
         f"{indent}}}\n        ")
s = s[:close].rstrip() + "\n" + clamp + s[close:]
p.write_text(s)
print("Patch applied")
