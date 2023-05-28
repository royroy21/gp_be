# Redis server
Redis server is created using the configs provided so to stop
the `WARNING Memory overcommit must be enabled!` warning. This
is fixed by setting `vm.overcommit_memory = 1` at the `init.sh`
file.

### Warning when running production
This configuration has `protected-mode no` as it isn't public
facing. In production this should be set to `protected-mode yes`
and an admin user should be configured.

###### Fixes were inspired by https://r-future.github.io/post/how-to-fix-redis-warnings-with-docker/
