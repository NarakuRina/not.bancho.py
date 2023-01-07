from __future__ import annotations

import textwrap
from typing import Any
from typing import Optional

import app.state.services

# +--------------+------------------------+------+-----+---------+-------+
# | Field        | Type                   | Null | Key | Default | Extra |
# +--------------+------------------------+------+-----+---------+-------+
# | server       | enum('osu!','private') | NO   | PRI | osu!    |       |
# | id           | int                    | NO   | PRI | NULL    |       |
# | set_id       | int                    | NO   |     | NULL    |       |
# | status       | int                    | NO   |     | NULL    |       |
# | md5          | char(32)               | NO   | UNI | NULL    |       |
# | artist       | varchar(128)           | NO   |     | NULL    |       |
# | title        | varchar(128)           | NO   |     | NULL    |       |
# | version      | varchar(128)           | NO   |     | NULL    |       |
# | creator      | varchar(19)            | NO   |     | NULL    |       |
# | filename     | varchar(256)           | NO   |     | NULL    |       |
# | last_update  | datetime               | NO   |     | NULL    |       |
# | total_length | int                    | NO   |     | NULL    |       |
# | max_combo    | int                    | NO   |     | NULL    |       |
# | frozen       | tinyint(1)             | NO   |     | 0       |       |
# | plays        | int                    | NO   |     | 0       |       |
# | passes       | int                    | NO   |     | 0       |       |
# | mode         | tinyint(1)             | NO   |     | 0       |       |
# | bpm          | float(12,2)            | NO   |     | 0.00    |       |
# | cs           | float(4,2)             | NO   |     | 0.00    |       |
# | ar           | float(4,2)             | NO   |     | 0.00    |       |
# | od           | float(4,2)             | NO   |     | 0.00    |       |
# | hp           | float(4,2)             | NO   |     | 0.00    |       |
# | diff         | float(6,3)             | NO   |     | 0.000   |       |
# +--------------+------------------------+------+-----+---------+-------+

READ_PARAMS = textwrap.dedent(
    """\
        server, id, set_id, status, md5, artist, title, version, creator, filename,
        last_update, total_length, max_combo, frozen, plays, passes, mode, bpm, cs,
        ar, od, hp, diff
    """,
)


async def create(
    server: str,
    id: int,
    set_id: int,
    status: int,
    md5: str,
    artist: str,
    title: str,
    version: str,
    creator: str,
    filename: str,
    last_update: str,
    total_length: int,
    max_combo: int,
    frozen: int,
    plays: int,
    passes: int,
    mode: int,
    bpm: float,
    cs: float,
    ar: float,
    od: float,
    hp: float,
    diff: float,
) -> dict[str, Any]:
    """Create a new beatmap entry in the database."""
    query = f"""\
        INSERT INTO beatmaps (
            server, id, set_id, status, md5, artist, title, version, creator, filename,
            last_update, total_length, max_combo, frozen, plays, passes, mode, bpm, cs,
            ar, od, hp, diff
        )
        VALUES (
            :server, :id, :set_id, :status, :md5, :artist, :title, :version, :creator,
            :filename, :last_update, :total_length, :max_combo, :frozen, :plays, :passes,
            :mode, :bpm, :cs, :ar, :od, :hp, :diff
        )
    """
    params = {
        "server": server,
        "id": id,
        "set_id": set_id,
        "status": status,
        "md5": md5,
        "artist": artist,
        "title": title,
        "version": version,
        "creator": creator,
        "filename": filename,
        "last_update": last_update,
        "total_length": total_length,
        "max_combo": max_combo,
        "frozen": frozen,
        "plays": plays,
        "passes": passes,
        "mode": mode,
        "bpm": bpm,
        "cs": cs,
        "ar": ar,
        "od": od,
        "hp": hp,
        "diff": diff,
    }
    rec_id = await app.state.services.database.execute(query, params)

    query = f"""\
        SELECT {READ_PARAMS}
          FROM beatmaps
         WHERE id = :id
    """
    params = {"id": rec_id}
    rec = await app.state.services.database.fetch_one(query, params)
    assert rec is not None
    return dict(rec)


async def fetch_one(
    server: str,
    id: int,
) -> Optional[dict[str, Any]]:
    """Fetch a beatmap entry from the database."""
    if id is None and server is None:
        raise ValueError("Must provide at least one parameter.")

    query = f"""\
        SELECT {READ_PARAMS}
          FROM beatmaps
         WHERE server = :server
              AND id = :id
    """
    params = {
        "id": id,
        "server": server,
    }
    rec = await app.state.services.database.fetch_one(query, params)
    return dict(rec) if rec is not None else None


async def fetch_count(
    set_id: Optional[int] = None,
    status: Optional[int] = None,
    artist: Optional[str] = None,
    creator: Optional[str] = None,
    filename: Optional[str] = None,
    mode: Optional[int] = None,
    frozen: Optional[int] = None,
) -> int:
    """Fetch the number of beatmaps in the database."""
    query = """\
        SELECT COUNT(*) AS count
            FROM beatmaps
        WHERE set_id = COALESCE(:set_id, set_id)
            AND status = COALESCE(:status, status)
            AND artist = COALESCE(:artist, artist)
            AND creator = COALESCE(:creator, creator)
            AND filename = COALESCE(:filename, filename)
            AND mode = COALESCE(:mode, mode)
            AND frozen = COALESCE(:frozen, frozen)

    """
    params = {
        "set_id": set_id,
        "status": status,
        "artist": artist,
        "creator": creator,
        "filename": filename,
        "mode": mode,
        "frozen": frozen,
    }
    rec = await app.state.services.database.fetch_one(query)
    assert rec is not None
    return rec["count"]


async def fetch_many(
    set_id: Optional[int] = None,
    status: Optional[int] = None,
    artist: Optional[str] = None,
    creator: Optional[str] = None,
    filename: Optional[str] = None,
    mode: Optional[int] = None,
    frozen: Optional[int] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
) -> list[dict[str, Any]]:
    """Fetch a list of beatmaps from the database."""
    query = f"""\
        SELECT {READ_PARAMS}
            FROM beatmaps
        WHERE set_id = COALESCE(:set_id, set_id)
            AND status = COALESCE(:status, status)
            AND artist = COALESCE(:artist, artist)
            AND creator = COALESCE(:creator, creator)
            AND filename = COALESCE(:filename, filename)
            AND mode = COALESCE(:mode, mode)
            AND frozen = COALESCE(:frozen, frozen)
    """
    params = {
        "set_id": set_id,
        "status": status,
        "artist": artist,
        "creator": creator,
        "filename": filename,
        "mode": mode,
        "frozen": frozen,
    }

    if page is not None and page_size is not None:
        query += """\
            LIMIT :limit
           OFFSET :offset
        """
        params["limit"] = page_size
        params["offset"] = (page - 1) * page_size

    recs = await app.state.services.database.fetch_all(query, params)
    return [dict(rec) for rec in recs]


async def update(
    server: str,
    id: int,
    set_id: Optional[int] = None,
    status: Optional[int] = None,
    md5: Optional[str] = None,
    artist: Optional[str] = None,
    title: Optional[str] = None,
    version: Optional[str] = None,
    creator: Optional[str] = None,
    filename: Optional[str] = None,
    last_update: Optional[str] = None,
    total_length: Optional[int] = None,
    max_combo: Optional[int] = None,
    frozen: Optional[int] = None,
    plays: Optional[int] = None,
    passes: Optional[int] = None,
    mode: Optional[int] = None,
    bpm: Optional[float] = None,
    cs: Optional[float] = None,
    ar: Optional[float] = None,
    od: Optional[float] = None,
    hp: Optional[float] = None,
    diff: Optional[float] = None,
) -> Optional[dict[str, Any]]:
    """Update a beatmap entry in the database."""
    query = f"""\
        UPDATE beatmaps
           SET set_id = COALESCE(:set_id, set_id),
               status = COALESCE(:status, status),
               md5 = COALESCE(:md5, md5),
               artist = COALESCE(:artist, artist),
               title = COALESCE(:title, title),
               version = COALESCE(:version, version),
               creator = COALESCE(:creator, creator),
               filename = COALESCE(:filename, filename),
               last_update = COALESCE(:last_update, last_update),
               total_length = COALESCE(:total_length, total_length),
               max_combo = COALESCE(:max_combo, max_combo),
               frozen = COALESCE(:frozen, frozen),
               plays = COALESCE(:plays, plays),
               passes = COALESCE(:passes, passes),
               mode = COALESCE(:mode, mode),
               bpm = COALESCE(:bpm, bpm),
               cs = COALESCE(:cs, cs),
               ar = COALESCE(:ar, ar),
               od = COALESCE(:od, od),
               hp = COALESCE(:hp, hp),
               diff = COALESCE(:diff, diff)
         WHERE server = :server
           AND id = :id
    """
    params = {
        "id": id,
        "server": server,
        "set_id": set_id,
        "status": status,
        "md5": md5,
        "artist": artist,
        "title": title,
        "version": version,
        "creator": creator,
        "filename": filename,
        "last_update": last_update,
        "total_length": total_length,
        "max_combo": max_combo,
        "frozen": frozen,
        "plays": plays,
        "passes": passes,
        "mode": mode,
        "bpm": bpm,
        "cs": cs,
        "ar": ar,
        "od": od,
        "hp": hp,
        "diff": diff,
    }
    await app.state.services.database.execute(query, params)

    query = f"""\
        SELECT {READ_PARAMS}
            FROM beatmaps
        WHERE server = :server
            AND id = :id
    """
    params = {
        "id": id,
        "server": server,
    }
    rec = await app.state.services.database.fetch_one(query, params)
    return dict(rec) if rec is not None else None


async def delete(server: str, id: int) -> Optional[dict[str, Any]]:
    """Delete a beatmap entry from the database."""
    query = f"""\
        SELECT {READ_PARAMS}
            FROM beatmaps
        WHERE server = :server
            AND id = :id
    """
    params = {
        "id": id,
        "server": server,
    }
    rec = await app.state.services.database.fetch_one(query, params)
    if rec is None:
        return None

    query = f"""\
        DELETE FROM beatmaps
        WHERE server = :server
            AND id = :id
    """
    params = {
        "id": id,
        "server": server,
    }
    await app.state.services.database.execute(query, params)
    return dict(rec)
