#!/bin/sh
# Run with the postgres:16-alpine image. The recovery share must support durable sync and atomic rename.
set -eu
umask 077

case "${1:-}" in
    archive)
        source_path=${2:?WAL source}
        destination=/recovery/wal/${3:?WAL segment}
        mkdir -p /recovery/wal
        if [ -e "$destination" ]; then
            cmp -s "$source_path" "$destination"
            sync -f /recovery/wal
            exit
        fi
        pending="$destination.pending"
        cp "$source_path" "$pending"
        sync "$pending"
        mv "$pending" "$destination"
        sync -f /recovery/wal
        ;;
    base)
        backup_id="$(date -u +%Y%m%dT%H%M%SZ)-$$"
        mkdir -p /recovery/base
        backup_dir="/recovery/base/$backup_id"
        mkdir "$backup_dir.pending"
        pg_basebackup -U "$POSTGRES_USER" -D "$backup_dir.pending" -X stream -c fast -w
        pg_verifybackup "$backup_dir.pending"
        mv "$backup_dir.pending" "$backup_dir"
        sync -f /recovery/base
        printf '%s\n' "$backup_id"
        ;;
    restore)
        backup_id=${2:?Verified backup ID}
        target_time=${3:?Point-in-time target with UTC offset}
        case "$backup_id" in
            *[!0-9TZ-]*) printf '%s\n' 'Invalid backup ID' >&2; exit 2 ;;
        esac
        if [ "$(id -u)" = 0 ]; then
            install -d -m 700 -o postgres -g postgres "$PGDATA"
            exec su-exec postgres /bin/sh "$0" "$@"
        fi
        if [ -n "$(ls -A "$PGDATA")" ]; then
            printf '%s\n' 'Restore requires an empty PGDATA directory' >&2
            exit 2
        fi
        backup_dir="/recovery/base/$backup_id"
        pg_verifybackup "$backup_dir"
        cp -a "$backup_dir/." "$PGDATA/"
        chmod 0700 "$PGDATA"
        pid_file="$PGDATA/postmaster.pid"
        test ! -e "$pid_file"
        touch "$PGDATA/recovery.signal"
        exec postgres -c "listen_addresses=" -c archive_mode=off \
            -c "restore_command=cp '/recovery/wal/%f' '%p'" \
            -c "recovery_target_time=$target_time" -c recovery_target_action=promote
        ;;
    *)
        printf '%s\n' 'Usage: pitr.sh archive SOURCE SEGMENT | base | restore BACKUP_ID TARGET_TIME' >&2
        exit 2
        ;;
esac
