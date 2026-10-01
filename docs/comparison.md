# Comparison and watchlists

Back to the [README](../README.md).

## Comparing videos

`-compare` fetches up to 50 videos in a single API call and prints their
performance next to each other:

```bash
python src/YST.py -compare C7REVNM_EWY,Xknt3_QJY7o
```

```
     Video        Views      Likes  Comments   Like%  Comment%     Views/h
--------------------------------------------------------------------------------
C7REVNM_EWY     2 827 211    157 438       428   5.57%     0.02%    848.2M/h
Xknt3_QJY7o            43          3         0   6.98%     0.00%        13/h
C7REVNM_EWY = Meow Chef— anyone want to help the cat clean the table? (0:12)
```

- `Like%` and `Comment%` are likes and comments relative to views.
- `Views/h` is views divided by the video length, so short videos naturally
  show a huge rate; it shows `n/a` when a length is unknown.
- The legend under the table maps the short ID to the title and length.
- IDs that do not exist are listed below the table.

The same works as a sub-command with space-separated IDs:

```bash
python src/YST.py compare C7REVNM_EWY Xknt3_QJY7o https://youtu.be/2RJFvNU08-4
```

URLs are accepted and reduced to their ID first, so mixed input is fine.

## Comparing channels

`-compare_channels` does the same for channels, adding views per video:

```bash
python src/YST.py -compare_channels UClFN9LShD_Pv0wnSeUKbUZw,UCifZaTQPiHE2QRgEwDNfhug
```

```
              Channel              Subs          Views   Videos    Views/video
------------------------------------------------------------------------------------
UCifZaTQPiHE2QRgEwDNfhug          693        152 486      434           351
UClFN9LShD_Pv0wnSeUKbUZw   38 600 000 37 278 025 432    1 290    28 897 694
UCifZaTQPiHE2QRgEwDNfhug = Klubuntu
UClFN9LShD_Pv0wnSeUKbUZw = That Little Puff
```

`Views/video` is total views divided by the published video count, and shows
`n/a` for a channel with no public videos.

## Watchlist

`-watchlist` monitors several channels at once. The file takes one channel per
line, `#` starts a comment and `@handle` entries are resolved:

```
# watchlist.txt
UClFN9LShD_Pv0wnSeUKbUZw
@ThatLittlePuff
UCifZaTQPiHE2QRgEwDNfhug
```

```bash
python src/YST.py -watchlist watchlist.txt -sleep_time=60 -snapshot_time=300
```

```
UClFN9LShD_Pv0wnSeUKbUZw   subs   38 600 000   views   37 278 025 432   videos    1 290
UCifZaTQPiHE2QRgEwDNfhug   subs          693   views          152 486   videos      434
```

Details worth knowing:

- Each channel gets its own snapshots in the history database, so the
  dashboard, charts and export work per channel.
- Entries that resolve to the same channel are fetched only once, which is why
  `@ThatLittlePuff` and its channel ID collapse into one row.
- Channels that hide their subscriber count show `hidden` instead of zero.
- Watchlist mode tracks channel-level metrics; the per-video numbers need a
  single channel and video run.
- Each refresh costs one API call per channel, so keep `-sleep_time` sensible on
  long lists.

Stop a watchlist run with `Ctrl+C`; the snapshots stay in the database.