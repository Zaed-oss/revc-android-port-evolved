// Mounts the browser's private storage (OPFS) at /game and makes it the working directory,
// so the engine finds models/gta3.img, data/..., audio/... exactly like on a desktop install.
#ifdef __EMSCRIPTEN__
#include <emscripten/wasmfs.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

extern "C" void web_mount_game_fs(void)
{
	backend_t opfs = wasmfs_create_opfs_backend();
	int r = wasmfs_create_directory("/game", 0777, opfs);
	printf("[web] OPFS mount at /game: result=%d errno=%d\n", r, errno);
	if (chdir("/game") != 0)
		printf("[web] chdir /game failed: %s\n", strerror(errno));
	else
		printf("[web] working directory is /game\n");
	fflush(stdout);
}
#endif
