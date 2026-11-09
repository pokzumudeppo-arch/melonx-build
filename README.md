# melonx-build

Personal build of [MeloNX](https://git.ryujinx.app/projects/MeloNX) (GPLv3), with one change:
the GPU texture cache is capped at 1 GiB on iOS.

**Why:** the cache limit is 50% of what Vulkan reports as GPU memory. On iPhone, MoltenVK
reports nearly all unified RAM (7681 MiB on an 8 GB iPhone 15 Pro), giving a ~3.75 GiB cache.
The whole app is limited to ~6 GiB and guest DRAM alone uses 3+ GiB, so iOS kills the app
before the cache ever evicts anything. Untested on device; see `scripts/apply_patch.py`.

This repository contains only build scripts; the source is pulled from the official repository at build time.
