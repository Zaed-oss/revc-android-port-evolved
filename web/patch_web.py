#!/usr/bin/env python3
"""Idempotent build-time patches so the engine can be compiled with Emscripten.
Run from the repository root AFTER submodules are checked out. Prints what it changed."""
import sys, os

def patch(path, old, new, label):
    if not os.path.exists(path):
        print(f'[MISSING] {path}'); return False
    s = open(path, encoding='utf-8').read()
    if new in s:
        print(f'[ok-already] {label}'); return True
    if old not in s:
        print(f'[NOT FOUND] {label} ({path})'); return False
    open(path, 'w', encoding='utf-8').write(s.replace(old, new))
    print(f'[patched] {label}'); return True

ok = True
# 1) librw: do not look for desktop OpenGL under Emscripten
ok &= patch('vendor/librw/src/CMakeLists.txt', 'if(NOT ANDROID)\n        set(OpenGL_GL_PREFERENCE GLVND)',
            'if(NOT ANDROID AND NOT EMSCRIPTEN)\n        set(OpenGL_GL_PREFERENCE GLVND)', 'librw: skip find_package(OpenGL)')
# 2) librw: WebGL2 == GLES 3.0 only
old = '\t{ SDL_GL_CONTEXT_PROFILE_CORE, 3, 3 },\n\t{ SDL_GL_CONTEXT_PROFILE_CORE, 2, 1 },\n\t{ SDL_GL_CONTEXT_PROFILE_ES, 3, 1 },\n\t{ SDL_GL_CONTEXT_PROFILE_ES, 2, 0 },\n'
new = ('#ifdef __EMSCRIPTEN__\n\t{ SDL_GL_CONTEXT_PROFILE_ES, 3, 0 },\n#else\n' + old + '#endif\n')
p = 'vendor/librw/src/gl/gl3device.cpp'
if os.path.exists(p):
    s = open(p, encoding='utf-8').read()
    if '#ifdef __EMSCRIPTEN__\n\t{ SDL_GL_CONTEXT_PROFILE_ES, 3, 0 }' in s:
        print('[ok-already] librw: WebGL2 profile')
    elif old in s:
        open(p, 'w', encoding='utf-8').write(s.replace(old, new)); print('[patched] librw: WebGL2 profile (%d places)' % s.count(old))
    else:
        print('[NOT FOUND] librw: profiles array'); ok = False
else:
    print('[MISSING]', p); ok = False
# 3) engine: use the targets from web/emscripten.cmake instead of find_package()
ok &= patch('src/CMakeLists.txt', '    find_package(OpenAL REQUIRED)\n    if(TARGET OpenAL::OpenAL)',
            '    if(NOT TARGET OpenAL::OpenAL)\n        find_package(OpenAL REQUIRED)\n    endif()\n    if(TARGET OpenAL::OpenAL)', 'engine: OpenAL target')
ok &= patch('src/CMakeLists.txt', 'find_package(mpg123 REQUIRED)\ntarget_link_libraries',
            'if(NOT TARGET MPG123::libmpg123)\n    find_package(mpg123 REQUIRED)\nendif()\ntarget_link_libraries', 'engine: mpg123 target')

# 4) OpenAL EFX/alext headers: Emscripten's OpenAL lacks them; copy the repo's vendored ones into
#    web/include/AL (searched with -idirafter, so Emscripten's own al.h/alc.h still win).
import re
src_dir, dst_dir = 'vendor/openal-soft/include/AL', 'web/include/AL'
if os.path.isdir(src_dir):
    os.makedirs(dst_dir, exist_ok=True)
    for f in ('efx.h', 'efx-presets.h', 'efx-creative.h', 'alext.h'):
        sp = os.path.join(src_dir, f)
        if not os.path.exists(sp):
            print(f'[MISSING] {sp}'); ok = False; continue
        t = open(sp, encoding='utf-8', errors='replace').read()
        t = re.sub(r'#\s*include\s+"(al|alc)\.h"', r'#include <AL/\1.h>', t)
        pre = '#ifndef AL_APIENTRY\n#define AL_APIENTRY\n#endif\n#ifndef AL_API\n#define AL_API\n#endif\n'
        open(os.path.join(dst_dir, f), 'w', encoding='utf-8').write(pre + t)
    print('[patched] OpenAL EFX headers copied to', dst_dir)
else:
    print('[MISSING]', src_dir); ok = False

# 5) librw has no Engine::get/setRenderScale here (Android-only feature): stub them for the web build
ok &= patch('src/fakerw/fake.cpp', 'RwInt32 RwEngineGetRenderScale(void) { return Engine::getRenderScale(); }',
            'RwInt32 RwEngineGetRenderScale(void) { return 100; }', 'engine: render scale getter stub')
ok &= patch('src/fakerw/fake.cpp', 'RwBool RwEngineSetRenderScale(RwInt32 percent) { return Engine::setRenderScale(percent); }',
            'RwBool RwEngineSetRenderScale(RwInt32 percent) { (void)percent; return 1; }', 'engine: render scale setter stub')
print('RESULT:', 'all patches applied' if ok else 'SOME PATCHES FAILED - see above')
sys.exit(0 if ok else 1)
