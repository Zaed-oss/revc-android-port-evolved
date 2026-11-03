# Included right after every project() call (-DCMAKE_PROJECT_INCLUDE=web/emscripten.cmake).
# Provides the third-party targets the engine expects, using Emscripten's built-in ports.
if(EMSCRIPTEN)
  if(NOT TARGET SDL2::SDL2)
    add_library(SDL2::SDL2 INTERFACE IMPORTED GLOBAL)
    set_target_properties(SDL2::SDL2 PROPERTIES
      INTERFACE_COMPILE_OPTIONS "-sUSE_SDL=2"
      INTERFACE_LINK_OPTIONS "-sUSE_SDL=2")
  endif()
  if(NOT TARGET OpenAL::OpenAL)
    add_library(OpenAL::OpenAL INTERFACE IMPORTED GLOBAL)
    set_target_properties(OpenAL::OpenAL PROPERTIES INTERFACE_LINK_LIBRARIES "openal")
  endif()
  if(NOT TARGET MPG123::libmpg123)
    add_library(MPG123::libmpg123 INTERFACE IMPORTED GLOBAL)
    set_target_properties(MPG123::libmpg123 PROPERTIES
      INTERFACE_COMPILE_OPTIONS "--use-port=mpg123"
      INTERFACE_LINK_OPTIONS "--use-port=mpg123")
  endif()
endif()
