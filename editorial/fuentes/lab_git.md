# Laboratorio de Git (ART-001) — salidas reales

Ejecutado el 2026-10-27 con `git version 2.56.0.windows.2`. Identidad fija: `Ada <ada@example.com>`.
Las fechas se fijaron con `GIT_AUTHOR_DATE`/`GIT_COMMITTER_DATE` cuando se indica, para que los hashes sean reproducibles.

## Blob, tree, commit (fecha 2026-01-01T12:00:00+0000)

```
$ echo 'hola mundo' | git hash-object --stdin
24db42bb7b999597a72801da70efd5876059bc0b
$ git cat-file -t 24db42b  -> blob
$ git cat-file -s 24db42b  -> 11
$ python: sha1(b'blob 11\x00hola mundo\n') -> 24db42bb7b999597a72801da70efd5876059bc0b
$ python: zlib.decompress(objeto) -> b'blob 11\x00hola mundo\n'
$ git update-index --add --cacheinfo 100644 24db42b hola.txt ; git write-tree
10e30303e3aef2eed251953d04e58bb67d6c777a
$ git cat-file -p 10e3030
100644 blob 24db42bb7b999597a72801da70efd5876059bc0b	hola.txt
$ echo 'Primer commit' | git commit-tree 10e3030
fc720b7fb6da046161a1bea8a620832b6eab9c29
$ git cat-file -p fc720b7
tree 10e30303e3aef2eed251953d04e58bb67d6c777a
author Ada <ada@example.com> 1767268800 +0000
committer Ada <ada@example.com> 1767268800 +0000

Primer commit
$ git cat-file -s fc720b7 -> 156
$ git update-ref refs/heads/main fc720b7 ; cat .git/refs/heads/main
fc720b7fb6da046161a1bea8a620832b6eab9c29
$ cat .git/HEAD -> ref: refs/heads/main
```

## Delta en un packfile (archivo de 400 líneas, una línea modificada)

```
$ git count-objects -v   (antes de gc)  count: 6  size: 2  in-pack: 0
$ git gc -q ; git count-objects -v      count: 0  size: 0  in-pack: 6  packs: 1  size-pack: 2
$ git verify-pack -v pack-*.idx
56cffe52829f6790e6a8583abe0f981a7fa137b6 blob   33611 1195 285
79df026f2f7869b14507329af7c78d0851cb68eb blob   18 30 1576 1 56cffe52829f6790e6a8583abe0f981a7fa137b6
non delta: 5 objects
chain length = 1: 1 object
tamaños: versión antigua = 33600 bytes ; versión nueva = 33611 bytes
```

La versión nueva (56cffe…) se guarda completa (1195 bytes comprimidos); la antigua (79df02…) se guarda como delta de 18 bytes (30 en el pack), profundidad 1, base = la nueva.

## Reflog y recuperación (fechas reales)

```
$ git reflog (tras 3 commits)
1a78706 HEAD@{0}: commit: Commit C
edc6699 HEAD@{1}: commit: Commit B
30347a4 HEAD@{2}: commit (initial): Commit A
$ git reset --hard HEAD~2 ; git reflog
30347a4 HEAD@{0}: reset: moving to HEAD~2
1a78706 HEAD@{1}: commit: Commit C
edc6699 HEAD@{2}: commit: Commit B
30347a4 HEAD@{3}: commit (initial): Commit A
$ git reset --hard 'HEAD@{1}'  -> vuelve a 1a78706 Commit C
```

## Objeto colgante y poda (reflog caducado a propósito)

```
$ git branch -D recuperada ; git reflog expire --expire=now --all
$ git fsck --lost-found
dangling commit d9f7408eea5f2373577451e72230551c8a7c0f2e
$ git gc -q --prune=now ; git count-objects -v   in-pack: 3 (antes 6)
```

## Merge con dos padres, etiqueta anotada, packed-refs

```
$ git cat-file -p HEAD   (merge --no-ff)
tree 033036e4414b4f7882f571c381b3cde88bc9f7f8
parent 1a787065968d794b6a2e7e1aa3e959aec8d46726
parent e12ca9e0b922e44d5d20a1192b64d6b13dc363cc
$ git tag -a v1.0 -m "Primera versión" ; cat .git/refs/tags/v1.0 ; git cat-file -t v1.0
123e8dcfe98db0ea4942cad16e589ba83cb7f6f2
tag
$ git cat-file -p v1.0
object 86007e628ea5d8d3c58cf9ecafd3b77786a44b39
type commit
tag v1.0
tagger Ada <ada@example.com> ...
$ git gc ; ls .git/refs/heads .git/refs/tags  -> vacíos
$ cat .git/packed-refs
# pack-refs with: peeled fully-peeled sorted
86007e628ea5d8d3c58cf9ecafd3b77786a44b39 refs/heads/main
e12ca9e0b922e44d5d20a1192b64d6b13dc363cc refs/heads/rama
123e8dcfe98db0ea4942cad16e589ba83cb7f6f2 refs/tags/v1.0
^86007e628ea5d8d3c58cf9ecafd3b77786a44b39
```

## SHA-256

```
$ git init --object-format=sha256 demo256 ; (commit)
$ git rev-parse HEAD
941de503f5ee7b61365a7e98989e93ed06dec137ee3c5baf5e77299f28588bf0   (64 caracteres hexadecimales)
$ git config extensions.objectformat -> sha256 ; git config core.repositoryformatversion -> 1
```

## Aviso de reproducibilidad

El primer intento de medir deltas (archivo escrito con CRLF y luego modificado con `sed`) quedó contaminado por la conversión de saltos de línea y se descartó; la medición final usa un archivo con LF y solo crece.
